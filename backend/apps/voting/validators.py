from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone

from apps.candidates.models import Candidate
from apps.elections.models import Election, Position, VotingChannel


def validate_election_is_open(election: Election):
    if election.status != Election.Status.OPEN:
        raise DjangoValidationError("Election is not open for voting.")
    now = timezone.now()
    if now < election.start_date:
        raise DjangoValidationError("Election voting has not started yet.")
    if now > election.end_date:
        raise DjangoValidationError("Election voting period has ended.")


def validate_channel_active(channel: VotingChannel):
    if not channel.is_active:
        raise DjangoValidationError("Voting channel is not active.")


def validate_channel_allowed_for_election(election: Election, channel: VotingChannel):
    if channel.channel_name == VotingChannel.ChannelName.WEB and not election.allow_web_voting:
        raise DjangoValidationError("Web voting is not enabled for this election.")
    if channel.channel_name == VotingChannel.ChannelName.USSD and not election.allow_ussd_voting:
        raise DjangoValidationError("USSD voting is not enabled for this election.")


def validate_candidate_for_ballot(candidate: Candidate, position: Position, election: Election):
    if candidate.election_id != election.id:
        raise DjangoValidationError("Candidate does not belong to this election.")
    if candidate.position_id != position.id:
        raise DjangoValidationError("Candidate does not belong to the selected position.")
    if candidate.status != Candidate.Status.APPROVED:
        raise DjangoValidationError("Candidate is not approved for voting.")
    if not position.is_active:
        raise DjangoValidationError("Position is not active.")
    if position.election_id != election.id:
        raise DjangoValidationError("Position does not belong to this election.")
