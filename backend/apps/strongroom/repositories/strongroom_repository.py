from apps.strongroom.models import (
    BallotSeal,
    CustodyRecord,
    ElectionSeal,
    IntegrityVerification,
)


class BallotSealRepository:
    def get_queryset(self):
        return BallotSeal.objects.select_related("election", "user").all()

    def get_by_svt(self, election, user, svt_id) -> BallotSeal | None:
        return self.get_queryset().filter(election=election, user=user, svt_id=svt_id).first()

    def create(self, **data) -> BallotSeal:
        return BallotSeal.objects.create(**data)

    def update(self, seal: BallotSeal, **fields) -> BallotSeal:
        for key, value in fields.items():
            setattr(seal, key, value)
        seal.save()
        return seal

    def list_for_election(self, election):
        return self.get_queryset().filter(election=election).order_by("-sealed_at")


class ElectionSealRepository:
    def get_queryset(self):
        return ElectionSeal.objects.select_related(
            "election", "election_result", "sealed_by", "locked_by"
        ).all()

    def get_by_election(self, election) -> ElectionSeal | None:
        return self.get_queryset().filter(election=election).first()

    def get_by_election_uuid(self, election_uuid) -> ElectionSeal | None:
        return self.get_queryset().filter(election__uuid=election_uuid).first()

    def get_by_verification_hash(self, verification_hash) -> ElectionSeal | None:
        return self.get_queryset().filter(verification_hash=verification_hash).first()

    def create(self, **data) -> ElectionSeal:
        return ElectionSeal.objects.create(**data)

    def update(self, seal: ElectionSeal, **fields) -> ElectionSeal:
        for key, value in fields.items():
            setattr(seal, key, value)
        seal.save()
        return seal


class CustodyRecordRepository:
    def create(self, **data) -> CustodyRecord:
        return CustodyRecord.objects.create(**data)

    def list_for_election(self, election):
        return CustodyRecord.objects.filter(election=election).select_related("actor").order_by(
            "timestamp"
        )


class IntegrityVerificationRepository:
    def create(self, **data) -> IntegrityVerification:
        return IntegrityVerification.objects.create(**data)

    def list_for_election(self, election, limit: int = 20):
        return (
            IntegrityVerification.objects.filter(election=election)
            .select_related("verified_by")
            .order_by("-verified_at")[:limit]
        )
