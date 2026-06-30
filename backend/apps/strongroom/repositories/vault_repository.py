from apps.strongroom.models import (
    StrongroomCommittee,
    StrongroomCommitteeMember,
    VaultAccessRequest,
    VaultSession,
)


class StrongroomCommitteeRepository:
    def get_by_election(self, election) -> StrongroomCommittee | None:
        return (
            StrongroomCommittee.objects.filter(election=election)
            .select_related("election", "nominated_by", "approved_by")
            .prefetch_related("members__user")
            .first()
        )

    def get_by_election_uuid(self, election_uuid) -> StrongroomCommittee | None:
        return (
            StrongroomCommittee.objects.filter(election__uuid=election_uuid)
            .select_related("election", "nominated_by", "approved_by")
            .prefetch_related("members__user")
            .first()
        )

    def get_or_create_for_election(self, election, **defaults) -> StrongroomCommittee:
        committee, _ = StrongroomCommittee.objects.get_or_create(
            election=election,
            defaults=defaults,
        )
        return committee

    def save(self, committee: StrongroomCommittee, **fields) -> StrongroomCommittee:
        for key, value in fields.items():
            setattr(committee, key, value)
        committee.save()
        return committee


class StrongroomCommitteeMemberRepository:
    def replace_members(self, committee: StrongroomCommittee, members: list[dict]) -> list:
        committee.members.all().delete()
        created = []
        for item in members:
            created.append(
                StrongroomCommitteeMember.objects.create(
                    committee=committee,
                    user_id=item["user_id"],
                    custodian_order=item["custodian_order"],
                )
            )
        return created


class VaultAccessRequestRepository:
    def create(self, **data) -> VaultAccessRequest:
        return VaultAccessRequest.objects.create(**data)

    def get_by_uuid(self, request_uuid) -> VaultAccessRequest | None:
        return (
            VaultAccessRequest.objects.filter(uuid=request_uuid)
            .select_related("election", "requested_by", "reviewed_by")
            .first()
        )

    def list_for_election(self, election):
        return VaultAccessRequest.objects.filter(election=election).select_related(
            "requested_by", "reviewed_by"
        )

    def save(self, request: VaultAccessRequest, **fields) -> VaultAccessRequest:
        for key, value in fields.items():
            setattr(request, key, value)
        request.save()
        return request


class VaultSessionRepository:
    def create(self, **data) -> VaultSession:
        return VaultSession.objects.create(**data)

    def get_by_uuid(self, session_uuid) -> VaultSession | None:
        return (
            VaultSession.objects.filter(uuid=session_uuid)
            .select_related("election", "access_request", "initiated_by")
            .first()
        )

    def get_active_for_election(self, election) -> VaultSession | None:
        return (
            VaultSession.objects.filter(
                election=election,
                status__in=[VaultSession.Status.AWAITING_CUSTODIANS, VaultSession.Status.ACTIVE],
            )
            .order_by("-created_at")
            .first()
        )

    def save(self, session: VaultSession, **fields) -> VaultSession:
        for key, value in fields.items():
            setattr(session, key, value)
        session.save()
        return session
