"""API ballot submit with skipped positions (empty candidate_uuids)."""

from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import Role, User
from apps.candidates.models import Candidate
from apps.elections.models import Election, Position, VoterEligibility
from apps.security.services.svt_service import svt_service
from apps.voting.services.presence_service import pre_vote_presence_service
from apps.voting.models import Vote
from django.core.files.uploadedfile import SimpleUploadedFile
from tests.integration.fixtures import ensure_voting_channels


def _capture_presence(election_uuid, student, token_code):
    image = SimpleUploadedFile(
        "presence.jpg",
        b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xd9",
        content_type="image/jpeg",
    )
    pre_vote_presence_service.submit_capture(election_uuid, student, token_code, image)


class BallotSubmitSkippedPositionApiTests(TestCase):
    def setUp(self):
        ensure_voting_channels()
        admin_role, _ = Role.objects.get_or_create(name=Role.Name.ADMIN)
        student_role, _ = Role.objects.get_or_create(name=Role.Name.STUDENT)
        self.admin = User.objects.create_user(
            email="skip-api-admin@ttu.edu.gh",
            password="unused",
            role=admin_role,
        )
        self.student = User.objects.create_user(
            email="skip-api-student@ttu.edu.gh",
            password="unused",
            role=student_role,
            phone_number="233249998877",
        )
        self.election = Election.objects.create(
            title="Multi Position Election",
            election_type=Election.ElectionType.STUDENT_UNION,
            status=Election.Status.OPEN,
            start_date=timezone.now() - timedelta(hours=1),
            end_date=timezone.now() + timedelta(days=1),
            allow_web_voting=True,
            created_by=self.admin,
        )
        self.president = Position.objects.create(
            election=self.election,
            title="President",
            max_votes_allowed=1,
            is_active=True,
        )
        self.secretary = Position.objects.create(
            election=self.election,
            title="Secretary",
            max_votes_allowed=1,
            is_active=True,
        )
        self.president_candidate = Candidate.objects.create(
            election=self.election,
            position=self.president,
            full_name="President Candidate",
            status=Candidate.Status.APPROVED,
        )
        Candidate.objects.create(
            election=self.election,
            position=self.secretary,
            full_name="Secretary Candidate",
            status=Candidate.Status.APPROVED,
        )
        VoterEligibility.objects.create(
            election=self.election,
            user=self.student,
            is_eligible=True,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.student)

    @patch("apps.security.services.svt_service.SVTService._send_svt_sms")
    def test_submit_accepts_skipped_position_with_empty_candidate_list(self, mock_sms):
        issued = svt_service.request_svt(self.election.uuid, self.student)
        svt_service.validate_and_start_ballot(
            issued["token_code"],
            self.student,
            self.election.uuid,
        )
        _capture_presence(self.election.uuid, self.student, issued["token_code"])
        response = self.client.post(
            reverse("voting:submit-ballot", kwargs={"election_uuid": self.election.uuid}),
            {
                "token_code": issued["token_code"],
                "channel_name": "web",
                "selections": [
                    {
                        "position_uuid": str(self.president.uuid),
                        "candidate_uuids": [str(self.president_candidate.uuid)],
                    },
                    {
                        "position_uuid": str(self.secretary.uuid),
                        "candidate_uuids": [],
                    },
                ],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()["data"]
        self.assertTrue(data["confirmation_reference"].startswith("VTB-"))
        self.assertEqual(data.get("positions_skipped"), 1)
        self.assertEqual(Vote.objects.filter(user=self.student, election=self.election).count(), 1)
