import logging

from apps.elections.models import VotingChannel
from apps.elections.repositories.election_repository import VotingChannelRepository
from core.exceptions import ConflictError, NotFoundError, ValidationError

logger = logging.getLogger("votebridge")


class VotingChannelService:
    """Business logic for voting channel registry."""

    def __init__(self, repository: VotingChannelRepository | None = None):
        self.repository = repository or VotingChannelRepository()

    def list_channels(self, active_only: bool = False):
        if active_only:
            return self.repository.list_active()
        return self.repository.get_queryset()

    def get_channel(self, uuid) -> VotingChannel:
        channel = self.repository.get_by_uuid(uuid)
        if not channel:
            raise NotFoundError(
                message="Voting channel not found.",
                code="channel_not_found",
            )
        return channel

    def create_channel(self, channel_name: str, is_active: bool = True) -> VotingChannel:
        if channel_name not in VotingChannel.ChannelName.values:
            raise ValidationError(message="Invalid channel name.", code="invalid_channel")

        if self.repository.get_by_name(channel_name):
            raise ConflictError(
                message="Voting channel already exists.",
                code="channel_exists",
            )

        channel = self.repository.create(channel_name=channel_name, is_active=is_active)
        logger.info("Voting channel created: %s", channel.channel_name)
        return channel

    def update_channel(self, uuid, **data) -> VotingChannel:
        channel = self.get_channel(uuid)
        if "channel_name" in data and data["channel_name"] != channel.channel_name:
            if self.repository.get_by_name(data["channel_name"]):
                raise ConflictError(
                    message="Voting channel already exists.",
                    code="channel_exists",
                )
        return self.repository.update(channel, **data)

    def delete_channel(self, uuid) -> None:
        channel = self.get_channel(uuid)
        self.repository.delete(channel)
        logger.info("Voting channel deleted: %s", uuid)
