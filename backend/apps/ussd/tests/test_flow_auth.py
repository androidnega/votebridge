from django.test import TestCase, override_settings

from apps.accounts.models import Role, User
from apps.ussd.services.ussd_flow_service import UssdFlowService


USSD_CACHE = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}


@override_settings(
    USSD_SESSION_TIMEOUT_MINUTES=5,
    USSD_RATE_LIMIT_PER_MSISDN=100,
    CACHES=USSD_CACHE,
)
class UssdAuthIntegrationTests(TestCase):
    def setUp(self):
        self.student_role, _ = Role.objects.get_or_create(
            name=Role.Name.STUDENT, defaults={"description": "Student"}
        )
        self.student = User.objects.create_user(
            email="ussd-student@test.local",
            username="ussd-student",
            password="1234",
            index_number="BC/ITS/24/047",
            phone_number="233241234567",
            role=self.student_role,
        )

    def test_auth_flow_prompts_index_then_pin(self):
        service = UssdFlowService()
        service.handle_request(
            session_id="auth-flow",
            msisdn="233241234567",
            inputs=[],
            is_new_session=True,
        )
        service.handle_request(session_id="auth-flow", msisdn="233241234567", inputs=["1"])
        r_index = service.handle_request(
            session_id="auth-flow", msisdn="233241234567", inputs=["BC/ITS/24/047"]
        )
        self.assertIn("PIN", r_index.message)
        service.handle_request(session_id="auth-flow", msisdn="233241234567", inputs=["1234"])
        from apps.ussd.models import USSDSession

        session = USSDSession.objects.get(session_id="auth-flow")
        self.assertEqual(session.user_id, self.student.id)

    def test_invalid_pin_fails_session(self):
        service = UssdFlowService()
        service.handle_request(
            session_id="auth-fail",
            msisdn="233241234567",
            inputs=[],
            is_new_session=True,
        )
        service.handle_request(session_id="auth-fail", msisdn="233241234567", inputs=["1"])
        service.handle_request(session_id="auth-fail", msisdn="233241234567", inputs=["BC/ITS/24/047"])
        response = service.handle_request(
            session_id="auth-fail", msisdn="233241234567", inputs=["wrong"]
        )
        self.assertIn("END", response.message)
        from apps.ussd.models import USSDSession

        session = USSDSession.objects.get(session_id="auth-fail")
        self.assertEqual(session.status, USSDSession.Status.FAILED)
