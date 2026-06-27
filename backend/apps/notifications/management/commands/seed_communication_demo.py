"""
Seed communication demo data for development.

Run: python manage.py seed_communication_demo

Dev passwords for demo users are documented in seed_demo_data (when available).
"""

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.notifications.models import DeliveryLog, InAppNotification, NotificationTemplate


class Command(BaseCommand):
    help = "Seed sample notifications, delivery logs, and queue entries for development."

    def handle(self, *args, **options):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        users = list(User.objects.filter(is_active=True)[:10])
        if not users:
            self.stdout.write(self.style.WARNING("No users found. Create users first."))
            return

        template = NotificationTemplate.objects.filter(code="election_opening").first()
        template_code = template.code if template else "test_message"

        samples = [
            (DeliveryLog.Channel.SMS, DeliveryLog.Status.DELIVERED, "+233241234567"),
            (DeliveryLog.Channel.EMAIL, DeliveryLog.Status.DELIVERED, "kwame.mensah@ttu.edu.gh"),
            (DeliveryLog.Channel.SMS, DeliveryLog.Status.FAILED, "+233209876543"),
            (DeliveryLog.Channel.EMAIL, DeliveryLog.Status.PENDING, "ama.osei@ttu.edu.gh"),
            (DeliveryLog.Channel.SMS, DeliveryLog.Status.RETRYING, "+233551112233"),
        ]

        ghana_names = [
            ("Kwame", "Mensah", "BC/ITS/24/047"),
            ("Ama", "Osei", "BC/ITD/24/031"),
            ("Kofi", "Asante", "BC/ITN/24/112"),
            ("Abena", "Boateng", "BC/ICT/24/056"),
        ]

        created_logs = 0
        for i, (channel, status, recipient) in enumerate(samples):
            user = users[i % len(users)]
            DeliveryLog.objects.get_or_create(
                recipient=recipient,
                channel=channel,
                template_code=template_code,
                defaults={
                    "user": user,
                    "status": status,
                    "subject": "SRC Elections 2025",
                    "body_snapshot": f"Hello, this is a demo {channel} notification.",
                    "retry_count": 1 if status == DeliveryLog.Status.RETRYING else 0,
                    "delivered_at": timezone.now() if status == DeliveryLog.Status.DELIVERED else None,
                    "failed_at": timezone.now() if status == DeliveryLog.Status.FAILED else None,
                },
            )
            created_logs += 1

        created_notifications = 0
        for i, (first, last, index) in enumerate(ghana_names):
            user = users[i % len(users)]
            _, created = InAppNotification.objects.get_or_create(
                user=user,
                title=f"Welcome, {first}",
                defaults={
                    "body": f"Hello {first} {last} ({index}), your VoteBridge notification centre is active.",
                    "category": "welcome",
                    "is_read": i % 2 == 0,
                },
            )
            if created:
                created_notifications += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {created_logs} delivery log samples and {created_notifications} in-app notifications."
            )
        )
