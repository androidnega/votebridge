from apps.elections.services.election_service import ElectionService
from apps.elections.services.eligibility_service import VoterEligibilityService
from apps.elections.services.position_service import PositionService
from apps.elections.services.voting_channel_service import VotingChannelService

election_service = ElectionService()
position_service = PositionService()
eligibility_service = VoterEligibilityService()
voting_channel_service = VotingChannelService()
