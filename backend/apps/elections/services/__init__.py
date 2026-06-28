from apps.elections.services.election_readiness_service import (
    ElectionReadinessService,
    election_readiness_service,
)
from apps.elections.services.election_service import ElectionService
from apps.elections.services.eligibility_service import VoterEligibilityService
from apps.elections.services.position_service import PositionService
from apps.elections.services.voting_channel_service import VotingChannelService

election_service = ElectionService()
position_service = PositionService()
eligibility_service = VoterEligibilityService()
voting_channel_service = VotingChannelService()

__all__ = [
    "ElectionReadinessService",
    "ElectionService",
    "PositionService",
    "VoterEligibilityService",
    "VotingChannelService",
    "election_readiness_service",
    "election_service",
    "eligibility_service",
    "position_service",
    "voting_channel_service",
]
