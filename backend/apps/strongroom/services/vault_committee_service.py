import logging
from datetime import timedelta

from django.utils import timezone

from apps.accounts.models import Role, User
from apps.accounts.repositories.user_repository import UserRepository
from apps.elections.models import Election
from apps.strongroom.models import StrongroomCommittee
from apps.strongroom.repositories.vault_repository import (
    StrongroomCommitteeMemberRepository,
    StrongroomCommitteeRepository,
)
from apps.strongroom.services.custody_service import custody_service
from core.exceptions import PermissionDeniedError, ValidationError

logger = logging.getLogger("votebridge")

ALLOWED_DURATION_HOURS = {1, 2, 3, 4}
PRE_OPEN_STATUSES = {Election.Status.DRAFT, Election.Status.SCHEDULED}
COMMITTEE_STAFF_ROLES = {Role.Name.ADMIN, Role.Name.SUPER_ADMIN}


class VaultCommitteeService:
    def __init__(
        self,
        committee_repository: StrongroomCommitteeRepository | None = None,
        member_repository: StrongroomCommitteeMemberRepository | None = None,
        user_repository: UserRepository | None = None,
    ):
        self.committee_repository = committee_repository or StrongroomCommitteeRepository()
        self.member_repository = member_repository or StrongroomCommitteeMemberRepository()
        self.user_repository = user_repository or UserRepository()

    def get_committee(self, election) -> dict | None:
        committee = self.committee_repository.get_by_election(election)
        if not committee:
            return None
        return self._serialize(committee)

    def configure_committee(
        self,
        election,
        *,
        actor,
        member_user_uuids: list,
        session_duration_hours: int,
        access_policy: str = "multi_custodian",
    ) -> dict:
        self._ensure_pre_open(election)
        if session_duration_hours not in ALLOWED_DURATION_HOURS:
            raise ValidationError(
                message="Session duration must be 1, 2, 3, or 4 hours.",
                code="invalid_duration",
            )
        if len(member_user_uuids) < 2:
            raise ValidationError(
                message="At least two custodians are required.",
                code="insufficient_custodians",
            )

        committee = self.committee_repository.get_or_create_for_election(
            election,
            nominated_by=actor,
            status=StrongroomCommittee.Status.DRAFT,
        )
        if not committee.is_mutable:
            raise PermissionDeniedError(
                message="Committee configuration is locked for this election.",
                code="committee_locked",
            )

        members = self._resolve_members(member_user_uuids)
        self.committee_repository.save(
            committee,
            session_duration_hours=session_duration_hours,
            access_policy=access_policy,
            nominated_by=actor,
            status=StrongroomCommittee.Status.DRAFT,
        )
        self.member_repository.replace_members(
            committee,
            [
                {"user_id": user.pk, "custodian_order": index + 1}
                for index, user in enumerate(members)
            ],
        )
        committee.refresh_from_db()
        return self._serialize(committee)

    def submit_for_approval(self, election, *, actor) -> dict:
        self._ensure_pre_open(election)
        committee = self._get_mutable_committee(election)
        if committee.members.count() < 2:
            raise ValidationError(
                message="Nominate at least two custodians before submission.",
                code="insufficient_custodians",
            )
        self.committee_repository.save(
            committee,
            status=StrongroomCommittee.Status.PENDING_APPROVAL,
            nominated_by=actor,
        )
        custody_service.record(
            election=election,
            action="committee_submitted",
            actor=actor,
            entity_type="strongroom_committee",
            entity_uuid=committee.uuid,
            previous_state={},
            current_state={"status": committee.status},
            metadata={"member_count": committee.members.count()},
        )
        return self._serialize(committee)

    def approve_committee(self, election, *, actor) -> dict:
        self._ensure_pre_open(election)
        committee = self.committee_repository.get_by_election(election)
        if not committee:
            raise ValidationError(message="No committee configuration found.", code="not_found")
        if committee.status != StrongroomCommittee.Status.PENDING_APPROVAL:
            raise ValidationError(
                message="Committee is not pending approval.",
                code="invalid_status",
            )

        now = timezone.now()
        self.committee_repository.save(
            committee,
            status=StrongroomCommittee.Status.APPROVED,
            approved_by=actor,
            approved_at=now,
        )
        custody_service.record(
            election=election,
            action="committee_approved",
            actor=actor,
            entity_type="strongroom_committee",
            entity_uuid=committee.uuid,
            previous_state={"status": StrongroomCommittee.Status.PENDING_APPROVAL},
            current_state={"status": committee.status, "approved_at": now.isoformat()},
            metadata={"session_duration_hours": committee.session_duration_hours},
        )
        return self._serialize(committee)

    def lock_committee_on_election_open(self, election) -> None:
        committee = self.committee_repository.get_by_election(election)
        if not committee or committee.status != StrongroomCommittee.Status.APPROVED:
            return
        previous = committee.status
        self.committee_repository.save(committee, status=StrongroomCommittee.Status.LOCKED)
        custody_service.record(
            election=election,
            action="committee_locked",
            actor=None,
            entity_type="strongroom_committee",
            entity_uuid=committee.uuid,
            previous_state={"status": previous},
            current_state={"status": committee.status},
            metadata={"trigger": "election_opened"},
        )

    def _get_mutable_committee(self, election) -> StrongroomCommittee:
        committee = self.committee_repository.get_by_election(election)
        if not committee:
            raise ValidationError(message="No committee configuration found.", code="not_found")
        if not committee.is_mutable:
            raise PermissionDeniedError(
                message="Committee configuration is locked.",
                code="committee_locked",
            )
        return committee

    def _ensure_pre_open(self, election) -> None:
        if election.status not in PRE_OPEN_STATUSES:
            raise PermissionDeniedError(
                message="Committee configuration is only allowed before the election opens.",
                code="election_already_open",
            )

    def _resolve_members(self, user_uuids: list) -> list[User]:
        members = []
        for user_uuid in user_uuids:
            user = self.user_repository.get_by_uuid(user_uuid)
            if not user or not user.is_active:
                raise ValidationError(
                    message=f"Invalid custodian account: {user_uuid}",
                    code="invalid_custodian",
                )
            role_name = getattr(user.role, "name", None)
            if role_name not in COMMITTEE_STAFF_ROLES:
                raise ValidationError(
                    message="Custodians must be election administrators.",
                    code="invalid_custodian_role",
                )
            members.append(user)
        return members

    def _serialize(self, committee: StrongroomCommittee) -> dict:
        return {
            "uuid": str(committee.uuid),
            "election_uuid": str(committee.election.uuid),
            "status": committee.status,
            "session_duration_hours": committee.session_duration_hours,
            "access_policy": committee.access_policy,
            "is_mutable": committee.is_mutable,
            "nominated_by": committee.nominated_by.get_full_name() if committee.nominated_by else None,
            "approved_by": committee.approved_by.get_full_name() if committee.approved_by else None,
            "approved_at": committee.approved_at,
            "members": [
                {
                    "uuid": str(member.uuid),
                    "custodian_order": member.custodian_order,
                    "user_uuid": str(member.user.uuid),
                    "full_name": member.user.get_full_name(),
                    "email": member.user.email,
                }
                for member in committee.members.select_related("user").order_by("custodian_order")
            ],
        }


vault_committee_service = VaultCommitteeService()
