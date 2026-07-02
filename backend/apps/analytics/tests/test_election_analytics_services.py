"""Tests for election live trend and completed-election analytics services."""

from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.accounts.models import Role, User
from apps.analytics.services.election_live_trend_service import election_live_trend_service
from apps.analytics.services.election_results_analytics_service import (
    election_results_analytics_service,
)
from apps.candidates.models import Candidate
from apps.elections.models import Election, Position, VoterEligibility, VotingChannel
from core.exceptions import ValidationError
from tests.integration.fixtures import ensure_voting_channels


class ElectionAnalyticsServiceTests(TestCase):
    def setUp(self):
        ensure_voting_channels()
        self.web_channel = VotingChannel.objects.get(channel_name=VotingChannel.ChannelName.WEB)

        self.admin = User.objects.create_user(
            email="analytics-admin@test.com",
            password="testpass123",
            role=Role.objects.get(name=Role.Name.ADMIN),
        )
        self.student = User.objects.create_user(
            email="analytics-student@test.com",
            password="testpass123",
            role=Role.objects.get(name=Role.Name.STUDENT),
            index_number="TTU/ITS/24/001",
        )
        self.student_two = User.objects.create_user(
            email="analytics-student2@test.com",
            password="testpass123",
            role=Role.objects.get(name=Role.Name.STUDENT),
            index_number="TTU/ITS/24/002",
        )

        now = timezone.now()
        self.open_election = Election.objects.create(
            title="Analytics Open Election",
            status=Election.Status.OPEN,
            start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=30),
            allow_web_voting=True,
            created_by=self.admin,
        )
        self.closed_election = Election.objects.create(
            title="Analytics Closed Election",
            status=Election.Status.CLOSED,
            start_date=now - timedelta(days=60),
            end_date=now - timedelta(days=30),
            allow_web_voting=True,
            created_by=self.admin,
        )

        for election, voters in (
            (self.open_election, [self.student, self.student_two]),
            (self.closed_election, [self.student, self.student_two]),
        ):
            for voter in voters:
                VoterEligibility.objects.create(election=election, user=voter, is_eligible=True)

        self.position = Position.objects.create(
            election=self.open_election,
            title="President",
            display_order=1,
            max_votes_allowed=1,
            is_active=True,
        )
        self.closed_position = Position.objects.create(
            election=self.closed_election,
            title="President",
            display_order=1,
            max_votes_allowed=1,
            is_active=True,
        )

        self.candidate_a = Candidate.objects.create(
            election=self.open_election,
            position=self.position,
            full_name="Candidate Alpha",
            status=Candidate.Status.APPROVED,
        )
        self.candidate_b = Candidate.objects.create(
            election=self.open_election,
            position=self.position,
            full_name="Candidate Beta",
            status=Candidate.Status.APPROVED,
        )
        self.closed_candidate_a = Candidate.objects.create(
            election=self.closed_election,
            position=self.closed_position,
            full_name="Closed Alpha",
            status=Candidate.Status.APPROVED,
        )
        self.closed_candidate_b = Candidate.objects.create(
            election=self.closed_election,
            position=self.closed_position,
            full_name="Closed Beta",
            status=Candidate.Status.APPROVED,
        )

        from apps.voting.models import Vote

        vote_time = timezone.now()

        def create_vote(*, election, position, candidate, user):
            vote_hash = Vote.compute_vote_hash(
                election.pk,
                position.pk,
                candidate.pk,
                user.pk,
                self.web_channel.pk,
                vote_time.isoformat(),
            )
            return Vote.objects.create(
                election=election,
                position=position,
                candidate=candidate,
                user=user,
                channel=self.web_channel,
                vote_hash=vote_hash,
                timestamp=vote_time,
            )

        create_vote(
            election=self.open_election,
            position=self.position,
            candidate=self.candidate_a,
            user=self.student,
        )
        create_vote(
            election=self.closed_election,
            position=self.closed_position,
            candidate=self.closed_candidate_a,
            user=self.student,
        )
        create_vote(
            election=self.closed_election,
            position=self.closed_position,
            candidate=self.closed_candidate_b,
            user=self.student_two,
        )

    def test_live_trend_for_open_election(self):
        data = election_live_trend_service.get_live_trend(self.open_election.uuid)
        self.assertEqual(data["election_uuid"], str(self.open_election.uuid))
        self.assertEqual(len(data["positions"]), 1)
        self.assertEqual(data["positions"][0]["leader"]["full_name"], "Candidate Alpha")
        self.assertIn("charts", data)
        self.assertGreater(data["summary"]["total_votes_cast"], 0)

    def test_live_trend_rejects_closed_election(self):
        with self.assertRaises(ValidationError):
            election_live_trend_service.get_live_trend(self.closed_election.uuid)

    def test_results_analytics_for_closed_election(self):
        data = election_results_analytics_service.get_results_analytics(self.closed_election.uuid)
        self.assertEqual(data["election_uuid"], str(self.closed_election.uuid))
        self.assertEqual(len(data["positions"]), 1)
        self.assertEqual(data["summary"]["total_votes_cast"], 2)
        self.assertIn("charts", data)
        self.assertTrue(data["candidates"])

    def test_results_analytics_rejects_open_election(self):
        with self.assertRaises(ValidationError):
            election_results_analytics_service.get_results_analytics(self.open_election.uuid)
