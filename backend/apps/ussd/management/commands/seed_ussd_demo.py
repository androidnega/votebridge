"""Seed demo USSD sessions and request logs for development."""

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.ussd.models import USSDRequestLog, USSDSession


class Command(BaseCommand):
    help = "Seed demo USSD sessions (completed, failed, expired, active)."

    def handle(self, *args, **options):
        samples = [
            ("sess-demo-001", "233241234567", USSDSession.Status.COMPLETED, True, "MAIN_MENU"),
            ("sess-demo-002", "233209876543", USSDSession.Status.FAILED, False, "AUTH_PIN"),
            ("sess-demo-003", "233551112233", USSDSession.Status.EXPIRED, False, "VOTE_POSITION"),
            ("sess-demo-004", "233244455566", USSDSession.Status.ACTIVE, False, "MAIN_MENU"),
            ("sess-demo-005", "233277788899", USSDSession.Status.COMPLETED, True, "VOTE_CONFIRM"),
        ]

        index_numbers = [
            "BC/ITS/24/047",
            "BC/ITD/24/031",
            "BC/ITN/24/112",
            "BC/ICT/24/056",
        ]

        for i, (sid, msisdn, status, voted, step) in enumerate(samples):
            session, _ = USSDSession.objects.update_or_create(
                session_id=sid,
                defaults={
                    "msisdn": msisdn,
                    "status": status,
                    "current_step": step,
                    "completed_vote": voted,
                    "request_count": 3 + i,
                    "state_data": {"demo_index": index_numbers[i % len(index_numbers)]},
                    "ended_at": timezone.now() if status != USSDSession.Status.ACTIVE else None,
                },
            )
            USSDRequestLog.objects.get_or_create(
                session=session,
                carrier_session_id=sid,
                msisdn=msisdn,
                step_after=step,
                defaults={
                    "raw_input": "1*1",
                    "parsed_inputs": ["1", "1"],
                    "outcome": (
                        USSDRequestLog.Outcome.SUCCESS
                        if status == USSDSession.Status.COMPLETED
                        else USSDRequestLog.Outcome.ERROR
                    ),
                    "response_message": "CON Demo USSD response",
                    "duration_ms": 120 + i * 10,
                },
            )

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(samples)} USSD demo sessions."))
