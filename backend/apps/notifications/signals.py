import logging

logger = logging.getLogger("votebridge")


def connect_notification_signals():
    from django.db.models.signals import post_save, pre_save

    from apps.elections.models import Election
    from apps.fraud.models import FraudCase, SecurityAlert
    from apps.results.models import ElectionResult
    from apps.security.models import SVTToken

    from apps.notifications import event_handlers

    pre_save.connect(event_handlers.on_election_pre_save, sender=Election, dispatch_uid="comm_election_pre")
    post_save.connect(event_handlers.on_election_saved, sender=Election, dispatch_uid="comm_election")
    pre_save.connect(event_handlers.on_svt_pre_save, sender=SVTToken, dispatch_uid="comm_svt_pre")
    post_save.connect(event_handlers.on_svt_saved, sender=SVTToken, dispatch_uid="comm_svt")
    pre_save.connect(
        event_handlers.on_election_result_pre_save,
        sender=ElectionResult,
        dispatch_uid="comm_results_pre",
    )
    post_save.connect(
        event_handlers.on_election_result_saved,
        sender=ElectionResult,
        dispatch_uid="comm_results",
    )
    post_save.connect(
        event_handlers.on_security_alert_saved,
        sender=SecurityAlert,
        dispatch_uid="comm_security_alert",
    )
    post_save.connect(
        event_handlers.on_fraud_case_saved,
        sender=FraudCase,
        dispatch_uid="comm_fraud_case",
    )
