from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.security.models import SVTToken
from apps.ussd.models import USSDSession
from apps.ussd.services.ussd_flow_service import UssdFlowService
from apps.voting.models import Vote
from tests.integration.fixtures import (
    create_open_ussd_election,
    create_roles,
    create_test_users,
    ensure_voting_channels,
)


USSD_CACHE = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}


@override_settings(
    USSD_SESSION_TIMEOUT_MINUTES=5,
    USSD_RATE_LIMIT_PER_MSISDN=100,
    CACHES=USSD_CACHE,
    BIOMETRICS_INFERENCE_MODE="mock",
)
class StudentWebVotingE2ETests(TestCase):
    def setUp(self):
        ensure_voting_channels()
        roles = create_roles()
        self.admin, self.student = create_test_users(roles)
        self.election, self.position = create_open_ussd_election(
            admin=self.admin, student=self.student, title="Web Vote Election"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.student)

    def test_student_web_vote_flow(self):
        from apps.security.services.svt_service import svt_service

        svt = svt_service.request_svt(
            self.election.uuid, self.student, ip_address="127.0.0.1", user_agent="test"
        )
        svt_service.validate_and_start_ballot(
            svt["token_code"], self.student, self.election.uuid, ip_address="127.0.0.1"
        )
        ballot_url = reverse("voting:ballot", kwargs={"election_uuid": self.election.uuid})
        ballot_resp = self.client.get(ballot_url)
        self.assertEqual(ballot_resp.status_code, status.HTTP_200_OK)
        candidate_uuid = ballot_resp.json()["data"]["positions"][0]["candidates"][0]["uuid"]
        submit_url = reverse("voting:submit-ballot", kwargs={"election_uuid": self.election.uuid})
        submit_resp = self.client.post(
            submit_url,
            {
                "token_code": svt["token_code"],
                "channel_name": "web",
                "selections": [
                    {"position_uuid": str(self.position.uuid), "candidate_uuids": [candidate_uuid]}
                ],
            },
            format="json",
        )
        self.assertEqual(submit_resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Vote.objects.filter(user=self.student, election=self.election).exists())
        self.assertEqual(
            SVTToken.objects.filter(user=self.student, election=self.election).first().status,
            SVTToken.Status.USED,
        )


@override_settings(
    USSD_SESSION_TIMEOUT_MINUTES=5,
    USSD_RATE_LIMIT_PER_MSISDN=100,
    CACHES=USSD_CACHE,
)
class StudentUssdVotingE2ETests(TestCase):
    def setUp(self):
        roles = create_roles()
        self.admin, self.student = create_test_users(roles)
        self.election, self.position = create_open_ussd_election(
            admin=self.admin, student=self.student, title="USSD Vote Election"
        )
        self.service = UssdFlowService()

    def _dial(self, session_id, inputs, *, new=False):
        return self.service.handle_request(
            session_id=session_id,
            msisdn="233241234567",
            inputs=inputs,
            is_new_session=new,
        )

    @patch("apps.notifications.event_handlers._safe_dispatch")
    def test_student_ussd_vote_flow(self, mock_dispatch):
        self._dial("ussd-vote", [], new=True)
        self._dial("ussd-vote", ["1"])
        self._dial("ussd-vote", ["BC/ITD/24/031"])
        self._dial("ussd-vote", ["1234"])
        self._dial("ussd-vote", ["1"])
        self._dial("ussd-vote", ["1"])
        self._dial("ussd-vote", ["1"])
        final = self._dial("ussd-vote", ["1"])
        self.assertIn("END", final.message)
        self.assertIn("Vote recorded", final.message)
        session = USSDSession.objects.get(session_id="ussd-vote")
        self.assertTrue(session.completed_vote)
        self.assertTrue(Vote.objects.filter(user=self.student, election=self.election).exists())


@override_settings(BIOMETRICS_INFERENCE_MODE="mock")
class ElectionOfficerWorkflowTests(TestCase):
    def setUp(self):
        ensure_voting_channels()
        roles = create_roles()
        self.admin, self.student = create_test_users(roles)
        self.election, _ = create_open_ussd_election(admin=self.admin, student=self.student)
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

    def test_admin_can_view_ussd_dashboard(self):
        response = self.client.get(reverse("ussd:dashboard"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("active_sessions", response.json()["data"])

    def test_admin_can_list_ussd_sessions(self):
        response = self.client.get(reverse("ussd:session-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


@override_settings(BIOMETRICS_INFERENCE_MODE="mock")
class StrongroomWorkflowTests(TestCase):
    def setUp(self):
        ensure_voting_channels()
        roles = create_roles()
        self.admin, self.student = create_test_users(roles)
        self.election, self.position = create_open_ussd_election(admin=self.admin, student=self.student)
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

    def test_strongroom_dashboard_after_vote(self):
        from apps.security.services.svt_service import svt_service
        from apps.voting.services import vote_service

        svt = svt_service.request_svt(self.election.uuid, self.student)
        ballot = svt_service.validate_and_start_ballot(
            svt["token_code"], self.student, self.election.uuid
        )
        candidate_uuid = str(
            self.position.candidates.filter(status="approved").first().uuid
        )
        vote_service.submit_ballot(
            election_uuid=self.election.uuid,
            user=self.student,
            token_code=svt["token_code"],
            selections=[{"position_uuid": str(self.position.uuid), "candidate_uuids": [candidate_uuid]}],
            channel_name="web",
        )
        url = reverse("strongroom:strongroom-dashboard", kwargs={"election_uuid": self.election.uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("seal_status", response.json()["data"])
