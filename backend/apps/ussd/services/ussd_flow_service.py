import logging
import re
import time
from dataclasses import dataclass

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from apps.accounts.services.auth_service import AuthService
from apps.dashboard.services.dashboard_service import dashboard_service
from apps.elections.models import Election
from apps.elections.repositories.election_repository import ElectionRepository
from apps.elections.repositories.eligibility_repository import VoterEligibilityRepository
from apps.elections.services.eligibility_service import VoterEligibilityService
from apps.security.models import SVTToken
from apps.security.services.svt_service import svt_service
from apps.ussd.models import USSDRequestLog, USSDSession
from apps.ussd.repositories.ussd_repository import USSDRequestLogRepository, USSDSessionRepository
from apps.ussd.services import ussd_constants as steps
from apps.voting.services import ballot_service, vote_service
from core.exceptions import AuthenticationError, NotFoundError, PermissionDeniedError, ValidationError

logger = logging.getLogger("votebridge")

INDEX_PATTERN = re.compile(r"^[A-Z]{2}/[A-Z]{2,4}/\d{2}/\d{2,4}$", re.IGNORECASE)


@dataclass
class UssdResponse:
    message: str
    continue_session: bool = True


class UssdFlowService:
    """State machine for VoteBridge USSD menus — delegates to existing platform services."""

    def __init__(
        self,
        session_repository: USSDSessionRepository | None = None,
        log_repository: USSDRequestLogRepository | None = None,
        auth_service: AuthService | None = None,
        election_repository: ElectionRepository | None = None,
        eligibility_service: VoterEligibilityService | None = None,
    ):
        self.session_repository = session_repository or USSDSessionRepository()
        self.log_repository = log_repository or USSDRequestLogRepository()
        self.auth_service = auth_service or AuthService()
        self.election_repository = election_repository or ElectionRepository()
        self.eligibility_service = eligibility_service or VoterEligibilityService()
        self.eligibility_repository = VoterEligibilityRepository()

    def handle_request(
        self,
        *,
        session_id: str,
        msisdn: str,
        inputs: list[str],
        service_code: str = "",
        network: str = "",
        ip_address: str | None = None,
        is_new_session: bool = False,
    ) -> UssdResponse:
        start = time.monotonic()
        self._check_rate_limit(msisdn)
        self.session_repository.expire_stale(int(settings.USSD_SESSION_TIMEOUT_MINUTES))

        session = self.session_repository.get_by_session_id(session_id)
        recovery_status = None
        step_before = session.current_step if session else steps.WELCOME

        if not session:
            session = self._create_session(session_id, msisdn, service_code, network)
        elif session.status != USSDSession.Status.ACTIVE:
            session, recovery_status = self.session_repository.reset_session(
                session, msisdn=msisdn, service_code=service_code, network=network
            )
        elif is_new_session and session.request_count > 0:
            session, recovery_status = self.session_repository.reset_session(
                session, msisdn=msisdn, service_code=service_code, network=network
            )

        session.request_count += 1
        session.last_activity_at = timezone.now()
        user_input = inputs[-1].strip() if inputs else ""

        if session.current_step == steps.MAIN_MENU and user_input == "0":
            response = self._end_session(session, "Thank you for using VoteBridge.")
        elif user_input == "0":
            response = self._handle_back(session)
        elif session.current_step == steps.WELCOME:
            response = self._show_main_menu(session)
        elif session.current_step == steps.MAIN_MENU:
            response = self._handle_main_menu(session, user_input, ip_address)
        elif session.current_step == steps.AUTH_INDEX:
            response = self._handle_auth_index(session, user_input)
        elif session.current_step == steps.ELECTION_PIN:
            response = self._handle_election_pin(session, user_input, ip_address)
        elif session.current_step == steps.AUTH_PIN:
            response = self._handle_auth_pin(session, user_input, ip_address)
        elif session.current_step == steps.VOTE_LIST:
            response = self._handle_vote_list(session, user_input, ip_address)
        elif session.current_step == steps.VOTE_SELECT:
            response = self._handle_vote_select(session, user_input, ip_address)
        elif session.current_step == steps.VOTE_POSITION:
            response = self._handle_vote_position(session, user_input)
        elif session.current_step == steps.VOTE_CANDIDATE:
            response = self._handle_vote_candidate(session, user_input)
        elif session.current_step == steps.VOTE_REVIEW:
            response = self._handle_vote_review(session, user_input, ip_address)
        elif session.current_step == steps.VOTE_CONFIRM:
            response = self._handle_vote_confirm(session, user_input, ip_address)
        elif session.current_step == steps.STATUS_LIST:
            response = self._handle_status_list(session, user_input)
        elif session.current_step == steps.VERIFY_SVT:
            response = self._handle_verify_svt(session, user_input, ip_address)
        elif session.current_step == steps.INFO_LIST:
            response = self._handle_info_list(session, user_input)
        elif session.current_step == steps.INFO_DETAIL:
            response = self._handle_info_detail(session, user_input)
        elif session.current_step == steps.HELP:
            response = self._show_help(session)
        else:
            response = UssdResponse("END Invalid session state. Please dial again.", False)

        self._persist_session(session, response)
        duration_ms = int((time.monotonic() - start) * 1000)
        self._log_request(
            session=session,
            step_before=step_before,
            step_after=session.current_step,
            raw_input="*".join(inputs),
            parsed_inputs=inputs,
            response=response,
            duration_ms=duration_ms,
            ip_address=ip_address,
            recovery_status=recovery_status,
        )
        self._record_monitoring(session, response)
        return response

    def _create_session(self, session_id, msisdn, service_code, network) -> USSDSession:
        return self.session_repository.create(
            session_id=session_id,
            msisdn=msisdn,
            service_code=service_code,
            network=network,
            current_step=steps.WELCOME,
            state_data={"pending_auth_target": None},
        )

    def _show_main_menu(self, session) -> UssdResponse:
        session.current_step = steps.MAIN_MENU
        recovered = session.state_data.pop("_recovered_from", None)
        prefix = ""
        if recovered in (USSDSession.Status.EXPIRED, USSDSession.Status.ABANDONED):
            prefix = "Session expired. "

        menu_state = self._main_menu_state()
        if menu_state == "voting_unavailable":
            return UssdResponse(
                f"CON {prefix}VoteBridge\n\nVoting is temporarily unavailable.\n\n0. Exit",
                True,
            )
        if menu_state == "no_election":
            return UssdResponse(
                f"CON {prefix}VoteBridge\n\nNo election is currently open.\n\n"
                "1. Election Info\n0. Exit",
                True,
            )

        return UssdResponse(
            f"CON {prefix}Welcome to VoteBridge\n"
            "1. Vote\n"
            "2. My Vote\n"
            "3. Election Info\n"
            "0. Exit",
            True,
        )

    def _handle_main_menu(self, session, choice: str, ip_address) -> UssdResponse:
        menu_state = self._main_menu_state()

        if choice == "0":
            return self._end_session(session, "Thank you for using VoteBridge.")

        if menu_state == "voting_unavailable":
            return UssdResponse("CON Invalid option.\n\n0. Exit", True)

        if menu_state == "no_election":
            if choice == "1":
                return self._require_auth(session, steps.INFO_LIST, ip_address)
            return UssdResponse(
                "CON Invalid option.\n\n1. Election Info\n0. Exit",
                True,
            )

        target = steps.MENU_TARGETS.get(choice)
        if not target:
            return UssdResponse("CON Invalid option.\n" + self._main_menu_text(), True)

        return self._require_auth(session, target, ip_address)

    def _require_auth(self, session, target_step: str, ip_address) -> UssdResponse:
        user = self._get_user(session)
        if user:
            session.current_step = target_step
            return self._dispatch_authenticated(session, target_step, "", ip_address)

        session.state_data["pending_auth_target"] = target_step
        session.current_step = steps.AUTH_INDEX
        return UssdResponse("CON Enter your index number:\n(e.g. BC/ITS/24/047)\n0. Back")

    def _handle_auth_index(self, session, index_number: str) -> UssdResponse:
        if not index_number:
            return UssdResponse("CON Index number required.\n0. Back", True)
        normalized = index_number.upper().strip()
        if not INDEX_PATTERN.match(normalized):
            return UssdResponse(
                "CON Invalid index format.\nUse BC/PROG/YY/NNN\n0. Back",
                True,
            )
        try:
            user = self.auth_service.authenticate_student_for_ussd(
                index_number=normalized,
                msisdn=session.msisdn,
                user_agent="ussd",
            )
        except AuthenticationError as exc:
            session.status = USSDSession.Status.FAILED
            session.failure_reason = "authentication_failed"
            return UssdResponse(f"END {exc.message}", False)

        session.user = user
        session.state_data["auth_index"] = normalized
        session.state_data["user_uuid"] = str(user.uuid)
        target = session.state_data.pop("pending_auth_target", steps.MAIN_MENU)
        session.current_step = target
        return self._dispatch_authenticated(session, target, "", None)

    def _handle_auth_pin(self, session, pin: str, ip_address) -> UssdResponse:
        index_number = session.state_data.get("auth_index", "")
        try:
            user = self.auth_service.authenticate_student_for_ussd_legacy(
                index_number=index_number,
                password=pin,
                ip_address=ip_address,
                user_agent="ussd",
            )
        except AuthenticationError:
            session.status = USSDSession.Status.FAILED
            session.failure_reason = "authentication_failed"
            return UssdResponse("END Invalid index number or PIN.", False)

        session.user = user
        session.state_data["user_uuid"] = str(user.uuid)
        target = session.state_data.pop("pending_auth_target", steps.MAIN_MENU)
        session.current_step = target
        return self._dispatch_authenticated(session, target, "", ip_address)

    def _handle_election_pin(self, session, pin: str, ip_address) -> UssdResponse:
        if not pin or not pin.isdigit() or len(pin) != 6:
            return UssdResponse("CON Enter your 6-digit Election PIN:\n0. Back", True)

        user = self._get_user(session)
        election_uuid = session.state_data.get("election_uuid")
        if not user or not election_uuid:
            return self._show_main_menu(session)

        election = self.election_repository.get_by_uuid(election_uuid)
        if not election:
            return UssdResponse("END Election not found.", False)

        try:
            from apps.elections.services.election_pin_service import election_pin_service

            election_pin_service.verify_pin(election, user, pin)
        except AuthenticationError as exc:
            return UssdResponse(f"CON {exc.message}\n0. Back", True)
        except NotFoundError:
            return UssdResponse("CON No election PIN on file.\n0. Back", True)

        session.current_step = steps.VOTE_SELECT
        return self._handle_vote_select(session, "1", ip_address)

    def _dispatch_authenticated(self, session, step: str, user_input: str, ip_address) -> UssdResponse:
        handlers = {
            steps.VOTE_LIST: self._start_vote_list,
            steps.STATUS_LIST: self._start_status_list,
            steps.VERIFY_SVT: self._start_verify_svt,
            steps.INFO_LIST: self._start_info_list,
        }
        handler = handlers.get(step)
        if handler:
            return handler(session, ip_address)
        return self._show_main_menu(session)

    def _start_vote_list(self, session, ip_address) -> UssdResponse:
        user = self._get_user(session)
        elections = self._ussd_open_elections(user)
        if not elections:
            session.current_step = steps.MAIN_MENU
            return UssdResponse("CON No open USSD elections for you.\n0. Main menu", True)

        session.state_data["elections"] = [
            {"uuid": str(e.uuid), "title": e.title} for e in elections
        ]
        session.current_step = steps.VOTE_LIST
        lines = ["CON Select election:"]
        for i, e in enumerate(elections, 1):
            lines.append(f"{i}. {e.title[:30]}")
        lines.append("0. Main menu")
        return UssdResponse("\n".join(lines))

    def _handle_vote_list(self, session, choice: str, ip_address) -> UssdResponse:
        elections = session.state_data.get("elections", [])
        if not choice.isdigit() or int(choice) < 1 or int(choice) > len(elections):
            return UssdResponse("CON Invalid selection.\n0. Main menu", True)

        selected = elections[int(choice) - 1]
        session.state_data["election_uuid"] = selected["uuid"]
        session.current_step = steps.ELECTION_PIN
        return UssdResponse("CON Enter your Election PIN:\n0. Back")

    def _handle_vote_select(self, session, _choice: str, ip_address) -> UssdResponse:
        user = self._get_user(session)
        election_uuid = session.state_data.get("election_uuid")
        if not user or not election_uuid:
            return self._show_main_menu(session)

        if not self.eligibility_service.check_voter_eligible(election_uuid, user):
            session.current_step = steps.MAIN_MENU
            return UssdResponse("CON You are not eligible for this election.\n0. Main menu", True)

        status = dashboard_service.get_student_election_status(user, election_uuid)
        if status.get("ballot_submitted"):
            session.current_step = steps.MAIN_MENU
            return UssdResponse("CON You have already voted in this election.\n0. Main menu", True)

        try:
            svt_result = svt_service.request_svt(
                election_uuid, user, ip_address=ip_address, user_agent="ussd"
            )
            token_code = svt_result["token_code"]
            svt_service.validate_and_start_ballot(
                token_code, user, election_uuid, ip_address=ip_address, user_agent="ussd"
            )
            ballot = ballot_service.get_ballot(
                election_uuid, user, ip_address=ip_address, user_agent="ussd"
            )
        except (ValidationError, PermissionDeniedError, NotFoundError) as exc:
            session.status = USSDSession.Status.FAILED
            session.failure_reason = str(exc)
            return UssdResponse(f"END {exc.message}", False)

        positions = [
            {
                "uuid": p["uuid"],
                "title": p["title"],
                "max_votes": p.get("max_votes_allowed", 1),
                "candidates": [
                    {"uuid": c["uuid"], "name": c["full_name"]}
                    for c in p.get("candidates", [])
                ],
            }
            for p in ballot.get("positions", [])
            if not p.get("has_voted") and p.get("candidates")
        ]

        if not positions:
            return UssdResponse("END No positions available on your ballot.", False)

        session.state_data["vote"] = {
            "token_code": token_code,
            "election_uuid": election_uuid,
            "positions": positions,
            "position_index": 0,
            "selections": [],
            "current_candidates": [],
        }
        session.current_step = steps.VOTE_POSITION
        return self._show_position(session)

    def _show_position(self, session) -> UssdResponse:
        vote = session.state_data["vote"]
        idx = vote["position_index"]
        positions = vote["positions"]
        if idx >= len(positions):
            session.current_step = steps.VOTE_REVIEW
            return self._show_review(session)

        position = positions[idx]
        vote["current_candidates"] = position["candidates"]
        lines = [f"CON {position['title']}", "Select candidate:"]
        for i, c in enumerate(position["candidates"], 1):
            lines.append(f"{i}. {c['name'][:25]}")
        lines.append("0. Cancel")
        session.current_step = steps.VOTE_CANDIDATE
        return UssdResponse("\n".join(lines))

    def _handle_vote_position(self, session, _choice: str) -> UssdResponse:
        return self._show_position(session)

    def _handle_vote_candidate(self, session, choice: str) -> UssdResponse:
        vote = session.state_data["vote"]
        candidates = vote.get("current_candidates", [])
        if not choice.isdigit() or int(choice) < 1 or int(choice) > len(candidates):
            return UssdResponse("CON Invalid candidate.\n0. Cancel", True)

        selected = candidates[int(choice) - 1]
        position = vote["positions"][vote["position_index"]]
        vote["selections"].append(
            {
                "position_uuid": position["uuid"],
                "position_title": position["title"],
                "candidate_uuids": [selected["uuid"]],
                "candidate_name": selected["name"],
            }
        )
        vote["position_index"] += 1
        session.current_step = steps.VOTE_POSITION
        return self._show_position(session)

    def _show_review(self, session) -> UssdResponse:
        vote = session.state_data["vote"]
        lines = ["CON Review ballot:"]
        for i, sel in enumerate(vote["selections"], 1):
            lines.append(f"{i}. {sel['position_title']}: {sel['candidate_name'][:20]}")
        lines.append("1. Submit vote")
        lines.append("2. Cancel")
        session.current_step = steps.VOTE_REVIEW
        return UssdResponse("\n".join(lines))

    def _handle_vote_review(self, session, choice: str, ip_address) -> UssdResponse:
        if choice == "1":
            session.current_step = steps.VOTE_CONFIRM
            return UssdResponse("CON Confirm submission?\n1. Yes\n2. No", True)
        session.current_step = steps.MAIN_MENU
        return UssdResponse("CON Vote cancelled.\n0. Main menu", True)

    def _handle_vote_confirm(self, session, choice: str, ip_address) -> UssdResponse:
        if choice != "1":
            session.current_step = steps.MAIN_MENU
            return UssdResponse("CON Vote cancelled.\n0. Main menu", True)

        user = self._get_user(session)
        vote_state = session.state_data.get("vote", {})
        selections = [
            {"position_uuid": s["position_uuid"], "candidate_uuids": s["candidate_uuids"]}
            for s in vote_state.get("selections", [])
        ]

        try:
            result = vote_service.submit_ballot(
                election_uuid=vote_state["election_uuid"],
                user=user,
                token_code=vote_state["token_code"],
                selections=selections,
                channel_name="ussd",
                ip_address=ip_address,
                user_agent="ussd",
            )
        except (ValidationError, PermissionDeniedError, NotFoundError) as exc:
            session.status = USSDSession.Status.FAILED
            session.failure_reason = str(exc)
            return UssdResponse(f"END Vote failed: {exc.message}", False)

        session.completed_vote = True
        session.status = USSDSession.Status.COMPLETED
        session.state_data["last_token"] = vote_state["token_code"]
        sms_note = (
            "SMS confirmation will be sent."
            if getattr(user, "phone_number", "")
            else "Contact the Election Office for vote confirmation."
        )
        msg = (
            f"END Vote recorded for {result['election_title']}.\n"
            f"Positions: {result['positions_count']}.\n"
            f"{sms_note}"
        )
        return UssdResponse(msg, False)

    def _start_status_list(self, session, _ip_address) -> UssdResponse:
        user = self._get_user(session)
        overview = dashboard_service.get_student_overview(user)
        elections = overview.get("active_elections", [])
        if not elections:
            session.current_step = steps.MAIN_MENU
            return UssdResponse("CON No active elections.\n0. Main menu", True)

        lines = ["CON Your voting status:"]
        for i, row in enumerate(elections[:5], 1):
            lines.append(
                f"{i}. {row['election_title'][:22]} - {row['confirmation_status']}"
            )
        lines.append("0. Main menu")
        session.current_step = steps.STATUS_LIST
        session.state_data["status_rows"] = elections[:5]
        return UssdResponse("\n".join(lines))

    def _handle_status_list(self, session, _choice: str) -> UssdResponse:
        session.current_step = steps.MAIN_MENU
        return self._show_main_menu(session)

    def _start_verify_svt(self, session, _ip_address) -> UssdResponse:
        session.current_step = steps.VERIFY_SVT
        return UssdResponse("CON Enter your voting token:\n0. Main menu")

    def _handle_verify_svt(self, session, token: str, ip_address) -> UssdResponse:
        user = self._get_user(session)
        if not token:
            return UssdResponse("CON Token required.\n0. Main menu", True)

        try:
            result = svt_service.verify_vote_by_svt(
                token, user, ip_address=ip_address, user_agent="ussd"
            )
        except (ValidationError, NotFoundError, PermissionDeniedError) as exc:
            return UssdResponse(f"END Verification failed: {exc.message}", False)

        valid = "VALID" if result["is_valid"] else "INVALID"
        positions = ", ".join(result["positions_completed"][:3])
        return UssdResponse(
            f"END Verification {valid}.\n"
            f"{result['election_title']}\n"
            f"Positions: {positions}",
            False,
        )

    def _start_info_list(self, session, _ip_address) -> UssdResponse:
        user = self._get_user(session)
        elections = self._ussd_open_elections(user) + list(
            Election.objects.filter(
                status__in=[Election.Status.SCHEDULED, Election.Status.CLOSED],
            ).order_by("-start_date")[:5]
        )
        seen = set()
        unique = []
        for e in elections:
            if str(e.uuid) not in seen:
                seen.add(str(e.uuid))
                unique.append(e)

        session.state_data["info_elections"] = [
            {"uuid": str(e.uuid), "title": e.title} for e in unique[:8]
        ]
        lines = ["CON Election information:"]
        for i, e in enumerate(unique[:8], 1):
            lines.append(f"{i}. {e.title[:28]}")
        lines.append("0. Main menu")
        session.current_step = steps.INFO_LIST
        return UssdResponse("\n".join(lines))

    def _handle_info_list(self, session, choice: str) -> UssdResponse:
        elections = session.state_data.get("info_elections", [])
        if not choice.isdigit() or int(choice) < 1 or int(choice) > len(elections):
            return UssdResponse("CON Invalid selection.\n0. Main menu", True)

        session.state_data["info_uuid"] = elections[int(choice) - 1]["uuid"]
        session.current_step = steps.INFO_DETAIL
        return self._handle_info_detail(session, "1")

    def _handle_info_detail(self, session, _choice: str) -> UssdResponse:
        election = self.election_repository.get_by_uuid(session.state_data.get("info_uuid"))
        if not election:
            return UssdResponse("END Election not found.", False)

        position_count = election.positions.filter(is_active=True).count()
        msg = (
            f"END {election.title}\n"
            f"Status: {election.get_status_display()}\n"
            f"Starts: {election.start_date.strftime('%d %b %Y %H:%M') if election.start_date else 'TBA'}\n"
            f"Ends: {election.end_date.strftime('%d %b %Y %H:%M') if election.end_date else 'TBA'}\n"
            f"Positions: {position_count}\n"
            "Dial *code# to vote when open."
        )
        session.current_step = steps.MAIN_MENU
        return UssdResponse(msg, False)

    def _show_help(self, session) -> UssdResponse:
        session.current_step = steps.MAIN_MENU
        return UssdResponse(
            "CON VoteBridge Help\n"
            "1. Vote - cast your ballot\n"
            "2. Status - check voting progress\n"
            "3. Verify - confirm vote recorded\n"
            "4. Info - election details\n"
            "Use index number + PIN to login.\n"
            "0. Main menu",
            True,
        )

    def _handle_back(self, session) -> UssdResponse:
        session.current_step = steps.MAIN_MENU
        return self._show_main_menu(session)

    def _end_session(self, session, message: str) -> UssdResponse:
        session.status = USSDSession.Status.COMPLETED
        session.ended_at = timezone.now()
        return UssdResponse(f"END {message}", False)

    def _ussd_open_elections(self, user):
        elections = Election.objects.filter(
            status=Election.Status.OPEN,
            allow_ussd_voting=True,
        ).order_by("-start_date")
        return [e for e in elections if self.eligibility_repository.is_user_eligible(e, user)]

    def _get_user(self, session):
        if session.user_id:
            return session.user
        return None

    def _main_menu_text(self) -> str:
        menu_state = self._main_menu_state()
        if menu_state == "voting_unavailable":
            return "0. Exit"
        if menu_state == "no_election":
            return "1. Election Info\n0. Exit"
        return "1. Vote\n2. My Vote\n3. Election Info\n0. Exit"

    def _main_menu_state(self) -> str:
        """full | no_election | voting_unavailable"""
        open_elections = Election.objects.filter(status=Election.Status.OPEN)
        if not open_elections.exists():
            return "no_election"
        if not open_elections.filter(allow_ussd_voting=True).exists():
            return "voting_unavailable"
        return "full"

    def _persist_session(self, session, response: UssdResponse) -> None:
        if not response.continue_session and session.status == USSDSession.Status.ACTIVE:
            session.status = USSDSession.Status.COMPLETED
            session.ended_at = timezone.now()
        self.session_repository.save(session)

    def _log_request(self, **kwargs) -> None:
        session = kwargs["session"]
        response: UssdResponse = kwargs["response"]
        recovery_status = kwargs.get("recovery_status")
        outcome = USSDRequestLog.Outcome.SUCCESS
        if recovery_status in (USSDSession.Status.EXPIRED, USSDSession.Status.ABANDONED):
            outcome = USSDRequestLog.Outcome.TIMEOUT
        elif response.message.startswith("END") and session.status == USSDSession.Status.FAILED:
            outcome = USSDRequestLog.Outcome.ERROR

        self.log_repository.create(
            session=session,
            carrier_session_id=session.session_id,
            msisdn=session.msisdn,
            raw_input=kwargs.get("raw_input", ""),
            parsed_inputs=kwargs.get("parsed_inputs", []),
            step_before=kwargs.get("step_before", ""),
            step_after=session.current_step,
            response_message=response.message,
            continue_session=response.continue_session,
            outcome=outcome,
            duration_ms=kwargs.get("duration_ms", 0),
            ip_address=kwargs.get("ip_address"),
        )

    def _record_monitoring(self, session, response: UssdResponse) -> None:
        try:
            from apps.security.services.monitoring_service import monitoring_service

            monitoring_service.record_event(
                event_type="admin_action",
                user=session.user,
                metadata={
                    "action": "ussd_request",
                    "session_id": session.session_id,
                    "msisdn": session.msisdn,
                    "step": session.current_step,
                    "completed_vote": session.completed_vote,
                    "continue_session": response.continue_session,
                },
            )
        except Exception:
            logger.debug("USSD monitoring log skipped")

    def _check_rate_limit(self, msisdn: str) -> None:
        key = f"ussd:rate:{msisdn}"
        count = cache.get(key, 0)
        limit = int(settings.USSD_RATE_LIMIT_PER_MSISDN)
        window = int(settings.USSD_RATE_LIMIT_WINDOW_SECONDS)
        if count >= limit:
            raise ValidationError(message="Too many requests. Try again later.", code="rate_limited")
        cache.set(key, count + 1, timeout=window)


ussd_flow_service = UssdFlowService()
