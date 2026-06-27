import logging

from django.db import transaction

logger = logging.getLogger("votebridge")


def on_svt_consumed(sender, instance, **kwargs):
    from apps.security.models import SVTToken
    from apps.strongroom.services.strongroom_service import strongroom_service

    if instance.status != SVTToken.Status.USED:
        return

    def _seal():
        try:
            strongroom_service.seal_ballot_for_svt(instance)
        except Exception:
            logger.exception("Failed to seal ballot for SVT %s", instance.svt_id)

    transaction.on_commit(_seal)


def on_election_result_saved(sender, instance, **kwargs):
    from apps.results.models import ElectionResult
    from apps.strongroom.services.strongroom_service import election_seal_service

    if instance.status == ElectionResult.Status.CERTIFIED:
        def _seal_election():
            try:
                election_seal_service.seal_on_certification(instance)
            except Exception:
                logger.exception("Failed to seal election on certification %s", instance.uuid)

        transaction.on_commit(_seal_election)

    if instance.status == ElectionResult.Status.PUBLISHED:
        def _lock_election():
            try:
                election_seal_service.lock_election(
                    instance.election,
                    actor=instance.published_by,
                )
            except Exception:
                logger.exception("Failed to lock election on publish %s", instance.election.uuid)

        transaction.on_commit(_lock_election)
