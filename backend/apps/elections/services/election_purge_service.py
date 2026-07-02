"""Hard-delete election operational data (votes, results, tokens) before removing the election."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from django.db import transaction
from django.db.models import Q

from apps.elections.models import Election
from apps.fraud.models import FraudCase, SecurityAlert
from apps.results.models import ElectionResult
from apps.security.models import AuditLog, SVTToken
from apps.strongroom.models import (
    BallotSeal,
    ElectionSeal,
    VaultAccessRequest,
    VaultSession,
)
from apps.voting.models import PreVotePresenceCapture, Vote

logger = logging.getLogger("votebridge")


@dataclass
class ElectionPurgeSummary:
    votes: int = 0
    svt_tokens: int = 0
    ballot_seals: int = 0
    results: int = 0
    fraud_cases: int = 0
    security_alerts: int = 0

    def as_dict(self) -> dict:
        return {
            "votes_removed": self.votes,
            "svt_tokens_removed": self.svt_tokens,
            "ballot_seals_removed": self.ballot_seals,
            "results_removed": self.results,
            "fraud_cases_removed": self.fraud_cases,
            "security_alerts_removed": self.security_alerts,
        }


@dataclass
class OperationalDataResetSummary:
    elections_removed: int = 0
    votes_removed: int = 0
    results_removed: int = 0
    per_election: list[dict] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "elections_removed": self.elections_removed,
            "votes_removed": self.votes_removed,
            "results_removed": self.results_removed,
            "details": self.per_election,
        }


class ElectionPurgeService:
    """Remove protected election dependencies, then delete the election record."""

    @transaction.atomic
    def purge_election(self, election: Election) -> ElectionPurgeSummary:
        summary = ElectionPurgeSummary()

        summary.fraud_cases, _ = FraudCase.objects.filter(
            Q(election=election) | Q(related_alert__election=election)
        ).delete()
        summary.security_alerts, _ = SecurityAlert.objects.filter(election=election).delete()

        VaultSession.objects.filter(election=election).delete()
        VaultAccessRequest.objects.filter(election=election).delete()

        summary.votes, _ = Vote.objects.filter(election=election).delete()
        PreVotePresenceCapture.objects.filter(election=election).delete()
        summary.ballot_seals, _ = BallotSeal.objects.filter(election=election).delete()
        summary.svt_tokens, _ = SVTToken.objects.filter(election=election).delete()
        ElectionSeal.objects.filter(election=election).delete()
        summary.results, _ = ElectionResult.objects.filter(election=election).delete()

        AuditLog.objects.filter(election=election).update(election=None)

        election_uuid = election.uuid
        election.delete()
        logger.info("Purged election %s", election_uuid)
        return summary

    @transaction.atomic
    def reset_all_operational_data(self) -> OperationalDataResetSummary:
        summary = OperationalDataResetSummary()
        elections = list(Election.objects.order_by("created_at"))
        for election in elections:
            meta = {"election_uuid": str(election.uuid), "title": election.title}
            purge = self.purge_election(election)
            summary.elections_removed += 1
            summary.votes_removed += purge.votes
            summary.results_removed += purge.results
            summary.per_election.append({**meta, **purge.as_dict()})
        return summary


election_purge_service = ElectionPurgeService()
