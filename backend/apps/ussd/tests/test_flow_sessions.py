from datetime import timedelta

from django.test import TestCase, override_settings
from django.utils import timezone

from apps.ussd.models import USSDRequestLog, USSDSession
from apps.ussd.repositories.ussd_repository import USSDSessionRepository
from apps.ussd.services.ussd_flow_service import UssdFlowService


USSD_CACHE = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}


@override_settings(
    USSD_SESSION_TIMEOUT_MINUTES=5,
    USSD_RATE_LIMIT_PER_MSISDN=100,
    CACHES=USSD_CACHE,
)
class UssdFlowSessionTests(TestCase):
    def test_welcome_shows_main_menu(self):
        service = UssdFlowService()
        response = service.handle_request(
            session_id="test-session-1",
            msisdn="233241234567",
            inputs=[],
            is_new_session=True,
        )
        self.assertTrue(response.continue_session)
        self.assertIn("Vote", response.message)
        session = USSDSession.objects.get(session_id="test-session-1")
        self.assertEqual(session.current_step, "MAIN_MENU")
        self.assertEqual(USSDRequestLog.objects.filter(carrier_session_id="test-session-1").count(), 1)

    def test_exit_ends_session(self):
        service = UssdFlowService()
        service.handle_request(
            session_id="test-exit",
            msisdn="233241234567",
            inputs=[],
            is_new_session=True,
        )
        response = service.handle_request(
            session_id="test-exit",
            msisdn="233241234567",
            inputs=["6"],
        )
        self.assertFalse(response.continue_session)
        self.assertIn("END", response.message)

    def test_session_continuation_preserves_state(self):
        service = UssdFlowService()
        service.handle_request(
            session_id="cont-session",
            msisdn="233241234567",
            inputs=[],
            is_new_session=True,
        )
        service.handle_request(session_id="cont-session", msisdn="233241234567", inputs=["5"])
        session = USSDSession.objects.get(session_id="cont-session")
        self.assertEqual(session.request_count, 2)
        self.assertEqual(session.current_step, "MAIN_MENU")

    def test_expired_session_recovery_reuses_session_id(self):
        repo = USSDSessionRepository()
        session = repo.create(
            session_id="recovery-sess",
            msisdn="233241234567",
            current_step="AUTH_PIN",
            status=USSDSession.Status.EXPIRED,
            state_data={"vote": {"token_code": "abc"}},
            ended_at=timezone.now(),
        )
        service = UssdFlowService()
        response = service.handle_request(
            session_id="recovery-sess",
            msisdn="233241234567",
            inputs=[],
            is_new_session=True,
        )
        session.refresh_from_db()
        self.assertEqual(session.status, USSDSession.Status.ACTIVE)
        self.assertEqual(USSDSession.objects.filter(session_id="recovery-sess").count(), 1)
        self.assertIn("Session expired", response.message)
        self.assertEqual(
            USSDRequestLog.objects.filter(
                carrier_session_id="recovery-sess",
                outcome=USSDRequestLog.Outcome.TIMEOUT,
            ).count(),
            1,
        )

    def test_stale_active_session_marked_abandoned_when_voting(self):
        repo = USSDSessionRepository()
        session = repo.create(
            session_id="abandon-sess",
            msisdn="233241234567",
            current_step="VOTE_POSITION",
            status=USSDSession.Status.ACTIVE,
            state_data={"vote": {"token_code": "tok", "positions": []}},
            last_activity_at=timezone.now() - timedelta(minutes=10),
        )
        repo.expire_stale(5)
        session.refresh_from_db()
        self.assertEqual(session.status, USSDSession.Status.ABANDONED)

    def test_stale_active_session_marked_expired_without_vote(self):
        repo = USSDSessionRepository()
        session = repo.create(
            session_id="expire-sess",
            msisdn="233241234567",
            current_step="MAIN_MENU",
            status=USSDSession.Status.ACTIVE,
            last_activity_at=timezone.now() - timedelta(minutes=10),
        )
        repo.expire_stale(5)
        session.refresh_from_db()
        self.assertEqual(session.status, USSDSession.Status.EXPIRED)
