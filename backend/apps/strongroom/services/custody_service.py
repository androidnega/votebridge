import logging

from apps.strongroom.repositories.strongroom_repository import CustodyRecordRepository

logger = logging.getLogger("votebridge")


class CustodyService:
    """Records chain-of-custody actions for election integrity."""

    def __init__(self, repository: CustodyRecordRepository | None = None):
        self.repository = repository or CustodyRecordRepository()

    def record(
        self,
        *,
        election,
        action: str,
        previous_state: dict,
        current_state: dict,
        actor=None,
        entity_type: str = "",
        entity_uuid=None,
        metadata: dict | None = None,
    ):
        record = self.repository.create(
            election=election,
            actor=actor,
            action=action,
            entity_type=entity_type,
            entity_uuid=entity_uuid,
            previous_state=previous_state or {},
            current_state=current_state or {},
            metadata=metadata or {},
        )
        logger.info("Custody recorded: %s for election %s", action, election.uuid)
        return record

    def list_timeline(self, election):
        return list(self.repository.list_for_election(election))

    def verify_chain_consistency(self, election) -> dict:
        records = list(self.repository.list_for_election(election))
        if not records:
            return {"passed": True, "issues": [], "record_count": 0}

        issues = []
        by_entity: dict[str, dict] = {}
        for record in records:
            key = f"{record.entity_type}:{record.entity_uuid}"
            prior = by_entity.get(key)
            if prior and prior.get("current_state") != record.previous_state:
                issues.append(
                    {
                        "record_uuid": str(record.uuid),
                        "action": record.action,
                        "reason": "previous_state mismatch",
                    }
                )
            by_entity[key] = {
                "current_state": record.current_state,
                "action": record.action,
            }

        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "record_count": len(records),
        }


custody_service = CustodyService()
