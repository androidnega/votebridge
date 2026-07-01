import logging

from django.db import transaction

from apps.notifications.models import DeliveryLog
from apps.notifications.services.communication_service import communication_service

logger = logging.getLogger("votebridge")


def _user_context(user) -> dict:
    if not user:
        return {}
    return {
        "first_name": getattr(user, "first_name", "") or "",
        "last_name": getattr(user, "last_name", "") or "",
        "full_name": user.get_full_name() if hasattr(user, "get_full_name") else "",
        "email": getattr(user, "email", "") or "",
        "phone_number": getattr(user, "phone_number", "") or "",
    }


def _resolve_channels(user, election=None, include_sms: bool = True) -> list[str]:
    channels = [DeliveryLog.Channel.IN_APP]
    if getattr(user, "email", None):
        channels.append(DeliveryLog.Channel.EMAIL)
    if include_sms and getattr(user, "phone_number", None):
        if election is None or getattr(election, "allow_sms_notifications", True):
            channels.append(DeliveryLog.Channel.SMS)
    return channels


def _safe_dispatch(template_code, user, context, channels=None, election=None):
    if not user:
        return

    ctx = {**_user_context(user), **context}

    def _send():
        try:
            for channel in channels or _resolve_channels(user, election=election):
                recipient = (
                    user.email
                    if channel == DeliveryLog.Channel.EMAIL
                    else user.phone_number
                    if channel == DeliveryLog.Channel.SMS
                    else str(user.uuid)
                )
                if channel in {DeliveryLog.Channel.SMS, DeliveryLog.Channel.EMAIL} and not recipient:
                    continue

                communication_service.dispatch(
                    template_code=template_code,
                    channel=channel,
                    recipient=recipient or str(user.uuid),
                    context=ctx,
                    user=user,
                )
        except Exception:
            logger.exception("Failed to dispatch %s to user %s", template_code, user.pk)

    transaction.on_commit(_send)


def on_election_pre_save(sender, instance, **kwargs):
    from apps.elections.models import Election

    if instance.pk:
        previous = Election.objects.filter(pk=instance.pk).values_list("status", flat=True).first()
        instance._previous_status = previous
    else:
        instance._previous_status = None


def on_election_saved(sender, instance, **kwargs):
    from apps.elections.models import Election

    previous = getattr(instance, "_previous_status", None)
    if instance.status == Election.Status.OPEN and previous != Election.Status.OPEN:
        _notify_election_opened(instance)
    elif instance.status == Election.Status.CLOSED and previous != Election.Status.CLOSED:
        _notify_election_closed(instance)


def _notify_election_opened(election):
    from apps.elections.repositories.eligibility_repository import VoterEligibilityRepository

    repo = VoterEligibilityRepository()
    eligibilities = repo.get_eligible_voters_for_election(election, limit=500)
    context = {
        "election_name": election.title,
        "election_uuid": str(election.uuid),
        "start_date": election.start_date.isoformat() if election.start_date else "",
        "end_date": election.end_date.isoformat() if election.end_date else "",
    }
    for eligibility in eligibilities:
        _safe_dispatch("election_opening", eligibility.user, context, election=election)


def _notify_election_closed(election):
    from apps.elections.repositories.eligibility_repository import VoterEligibilityRepository

    repo = VoterEligibilityRepository()
    eligibilities = repo.get_eligible_voters_for_election(election, limit=500)
    context = {"election_name": election.title, "election_uuid": str(election.uuid)}
    for eligibility in eligibilities:
        _safe_dispatch("election_closing", eligibility.user, context, election=election)


def on_svt_pre_save(sender, instance, **kwargs):
    from apps.security.models import SVTToken

    if instance.pk:
        previous = SVTToken.objects.filter(pk=instance.pk).values_list("status", flat=True).first()
        instance._previous_status = previous
    else:
        instance._previous_status = None


def on_svt_saved(sender, instance, created, **kwargs):
    from apps.security.models import SVTToken

    previous = getattr(instance, "_previous_status", None)

    if instance.status == SVTToken.Status.ISSUED and (created or previous != SVTToken.Status.ISSUED):
        # Phase 56: SMS is sent from SVTService with the plain token code.
        pass

    if instance.status == SVTToken.Status.USED and previous != SVTToken.Status.USED:
        context = {
            "election_name": instance.election.title,
            "election_uuid": str(instance.election.uuid),
        }
        _safe_dispatch("vote_confirmation", instance.user, context, election=instance.election)


def on_election_result_pre_save(sender, instance, **kwargs):
    from apps.results.models import ElectionResult

    if instance.pk:
        previous = ElectionResult.objects.filter(pk=instance.pk).values_list("status", flat=True).first()
        instance._previous_status = previous
    else:
        instance._previous_status = None


def on_election_result_saved(sender, instance, **kwargs):
    from apps.results.models import ElectionResult

    previous = getattr(instance, "_previous_status", None)
    if instance.status != ElectionResult.Status.PUBLISHED or previous == ElectionResult.Status.PUBLISHED:
        return

    from apps.elections.repositories.eligibility_repository import VoterEligibilityRepository

    election = instance.election
    repo = VoterEligibilityRepository()
    eligibilities = repo.get_eligible_voters_for_election(election, limit=500)
    context = {
        "election_name": election.title,
        "election_uuid": str(election.uuid),
        "published_at": instance.published_at.isoformat() if instance.published_at else "",
    }
    for eligibility in eligibilities:
        _safe_dispatch("results_published", eligibility.user, context, election=election)


def on_security_alert_saved(sender, instance, created, **kwargs):
    if not created:
        return
    from apps.accounts.models import Role, User

    admins = User.objects.filter(
        role__name__in=[Role.Name.ADMIN, Role.Name.SUPER_ADMIN], is_active=True
    )
    context = {
        "alert_title": instance.title,
        "severity": instance.alert_type,
        "alert_uuid": str(instance.alert_id),
    }
    for admin in admins[:50]:
        _safe_dispatch(
            "security_alert",
            admin,
            context,
            channels=[DeliveryLog.Channel.IN_APP, DeliveryLog.Channel.EMAIL],
        )


def on_fraud_case_saved(sender, instance, created, **kwargs):
    if not created:
        return
    from apps.accounts.models import Role, User

    admins = User.objects.filter(
        role__name__in=[Role.Name.ADMIN, Role.Name.SUPER_ADMIN], is_active=True
    )
    case_title = instance.related_alert.title if instance.related_alert else str(instance.fraud_case_id)
    context = {
        "case_title": case_title,
        "severity": instance.severity,
        "case_uuid": str(instance.fraud_case_id),
    }
    for admin in admins[:50]:
        _safe_dispatch(
            "fraud_alert",
            admin,
            context,
            channels=[DeliveryLog.Channel.IN_APP, DeliveryLog.Channel.EMAIL],
        )
