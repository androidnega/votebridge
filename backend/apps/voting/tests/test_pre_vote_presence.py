"""Pre-vote web presence capture tests."""

from datetime import timedelta
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
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
from apps.voting.services.vote_service import BallotService, VoteService
from core.exceptions import PermissionDeniedError
from tests.integration.fixtures import ensure_voting_channels


def _sample_image():
    return SimpleUploadedFile(
        "presence.jpg",
        b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xd9",
        content_type="image/jpeg",
    )


class PreVotePresenceTests(TestCase):
    def setUp(self):
        ensure_voting_channels()
        admin_role, _ = Role.objects.get_or_create(name=Role.Name.ADMIN)
        student_role, _ = Role.objects.get_or_create(name=Role.Name.STUDENT)
        self.admin = User.objects.create_user(
            email="presence-admin@ttu.edu.gh",
            password="unused",
            role=admin_role,
        )
        self.student = User.objects.create_user(
            email="presence-student@ttu.edu.gh",
            password="unused",
            role=student_role,
            phone_number="233241112233",
        )
        self.election = Election.objects.create(
            title="SRC General Elections 2026",
            status=Election.Status.OPEN,
            start_date=timezone.now() - timedelta(hours=1),
            end_date=timezone.now() + timedelta(days=1),
            created_by=self.admin,
        )
        self.position = Position.objects.create(
            election=self.election,
            title="President",
            max_votes_allowed=1,
            is_active=True,
        )
        self.candidate = Candidate.objects.create(
            election=self.election,
            position=self.position,
            full_name="Presence Candidate",
            status=Candidate.Status.APPROVED,
        )
        VoterEligibility.objects.create(
            election=self.election,
            user=self.student,
            is_eligible=True,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.student)
        self.token_code = None

    def _validate_session(self):
        issued = svt_service.request_svt(self.election.uuid, self.student)
        self.token_code = issued["token_code"]
        svt_service.validate_and_start_ballot(
            self.token_code,
            self.student,
            self.election.uuid,
        )

    @patch("apps.security.services.svt_service.SVTService._send_svt_sms")
    def test_ballot_blocked_until_presence_captured(self, mock_sms):
        self._validate_session()
        with self.assertRaises(PermissionDeniedError) as ctx:
            BallotService().get_ballot(self.election.uuid, self.student)
        self.assertEqual(ctx.exception.code, "presence_required")

    @patch("apps.security.services.svt_service.SVTService._send_svt_sms")
    def test_presence_capture_unlocks_ballot(self, mock_sms):
        self._validate_session()
        pre_vote_presence_service.submit_capture(
            self.election.uuid,
            self.student,
            self.token_code,
            _sample_image(),
        )
        ballot = BallotService().get_ballot(self.election.uuid, self.student)
        self.assertTrue(ballot["ballot_session_active"])

    @patch("apps.security.services.svt_service.SVTService._send_svt_sms")
    def test_presence_status_and_api_capture(self, mock_sms):
        self._validate_session()
        status_response = self.client.get(
            reverse("voting:presence-status", kwargs={"election_uuid": self.election.uuid})
        )
        self.assertEqual(status_response.status_code, status.HTTP_200_OK)
        status_data = status_response.json()["data"]
        self.assertTrue(status_data["presence_required"])
        self.assertFalse(status_data["presence_captured"])

        capture_response = self.client.post(
            reverse("voting:presence-capture", kwargs={"election_uuid": self.election.uuid}),
            {
                "token_code": self.token_code,
                "channel": "web",
                "image": _sample_image(),
            },
            format="multipart",
        )
        self.assertEqual(capture_response.status_code, status.HTTP_201_CREATED)
        self.assertIn("captured_at", capture_response.json()["data"])

    @patch("apps.security.services.svt_service.SVTService._send_svt_sms")
    def test_web_submit_requires_presence(self, mock_sms):
        self._validate_session()
        with self.assertRaises(PermissionDeniedError):
            VoteService().submit_ballot(
                self.election.uuid,
                self.student,
                self.token_code,
                selections=[
                    {
                        "position_uuid": str(self.position.uuid),
                        "candidate_uuids": [str(self.candidate.uuid)],
                    },
                ],
                channel_name="web",
            )

        pre_vote_presence_service.submit_capture(
            self.election.uuid,
            self.student,
            self.token_code,
            _sample_image(),
        )
        confirmation = VoteService().submit_ballot(
            self.election.uuid,
            self.student,
            self.token_code,
            selections=[
                {
                    "position_uuid": str(self.position.uuid),
                    "candidate_uuids": [str(self.candidate.uuid)],
                },
            ],
            channel_name="web",
        )
        self.assertTrue(confirmation["confirmation_reference"].startswith("VTB-"))
