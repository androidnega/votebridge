from django.apps import AppConfig


class StrongroomConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.strongroom"
    label = "strongroom"
    verbose_name = "Strongroom"

    def ready(self):
        from apps.results.models import ElectionResult
        from apps.security.models import SVTToken
        from apps.strongroom import signals
        from django.db.models.signals import post_save

        post_save.connect(signals.on_svt_consumed, sender=SVTToken, dispatch_uid="strongroom_svt_seal")
        post_save.connect(
            signals.on_election_result_saved,
            sender=ElectionResult,
            dispatch_uid="strongroom_result_seal",
        )
