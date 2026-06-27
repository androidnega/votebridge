from datetime import timedelta
from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings
from django.utils import timezone

from apps.accounts.models import Role, User
from apps.candidates.models import Candidate
from apps.elections.models import Election, Position, VoterEligibility
from apps.ussd.services.ussd_flow_service import UssdFlowService
from tests.integration.fixtures import create_roles, create_test_users, ensure_voting_channels


USSD_CACHE = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}


@override_settings(
    USSD_SESSION_TIMEOUT_MINUTES=5,
    USSD_RATE_LIMIT_PER_MSISDN=100,
    CACHES=USSD_CACHE,
)
class UssdVotingFlowTests(TestCase):
    def setUp(self):
        ensure_voting_channels()
        roles = create_roles()
        self.admin, self.student = create_test_users(roles)
        now = timezone.now()
        self.election = Election.objects.create(
            title="USSD Flow Test",
            election_type=Election.ElectionType.STUDENT_UNION,
            start_date=now - timedelta(hours=1),
            end_date=now + timedelta(days=3),
            status=Election.Status.OPEN,
            allow_ussd_voting=True,
            created_by=self.admin,
        )
        self.position = Position.objects.create(
            election=self.election,
            title="SRC President",
            max_votes_allowed=1,
            is_active=True,
        )
        Candidate.objects.create(
            election=self.election,
            position=self.position,
            full_name="Candidate One",
            status=Candidate.Status.APPROVED,
        )
        VoterEligibility.objects.create(
            election=self.election,
            user=self.student,
            is_eligible=True,
            verified_by=self.admin,
            verified_at=now,
        )
        self.service = UssdFlowService()

    def _auth_and_reach_vote_list(self):
        self.service.handle_request(
            session_id="vote-flow", msisdn="233241234567", inputs=[], is_new_session=True
        )
        self.service.handle_request(session_id="vote-flow", msisdn="233241234567", inputs=["1"])
        self.service.handle_request(session_id="vote-flow", msisdn="233241234567", inputs=["BC/ITD/24/031"])
        self.service.handle_request(session_id="vote-flow", msisdn="233241234567", inputs=["1234"])

    def test_eligibility_blocks_ineligible_student(self):
        VoterEligibility.objects.filter(election=self.election, user=self.student).update(
            is_eligible=False
        )
        self._auth_and_reach_vote_list()
        response = self.service.handle_request(session_id="vote-flow", msisdn="233241234567", inputs=["1"])
        self.assertIn("No open USSD elections", response.message)

    @patch("apps.security.services.svt_service.svt_service.verify_vote_by_svt")
    def test_svt_verify_menu(self, mock_verify):
        mock_verify.return_value = {
            "is_valid": True,
            "election_title": self.election.title,
            "positions_completed": ["SRC President"],
        }
        self._auth_and_reach_vote_list()
        self.service.handle_request(session_id="vote-flow", msisdn="233241234567", inputs=["0"])
        self.service.handle_request(session_id="vote-flow", msisdn="233241234567", inputs=["3"])
        response = self.service.handle_request(session_id="vote-flow", msisdn="233241234567", inputs=["SVT-TEST"])
        self.assertIn("END", response.message)
        mock_verify.assert_called_once()
