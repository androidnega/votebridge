from django.urls import path

from apps.biometrics.api import views

app_name = "biometrics"

urlpatterns = [
    path("enrollment/", views.BiometricEnrollmentView.as_view(), name="enrollment"),
    path("enrollment/login/", views.BiometricEnrollLoginView.as_view(), name="enroll-login"),
    path("reset/otp/", views.BiometricResetOtpView.as_view(), name="reset-otp"),
    path("reset/", views.BiometricResetView.as_view(), name="reset"),
    path("verification/login/", views.BiometricVerifyLoginView.as_view(), name="verify-login"),
    path("verification/step-up/", views.BiometricStepUpView.as_view(), name="verify-step-up"),
    path("challenge/", views.BiometricChallengeView.as_view(), name="challenge"),
    path("status/", views.BiometricStatusView.as_view(), name="status"),
    path("settings/", views.BiometricSettingsView.as_view(), name="settings"),
    path("history/", views.BiometricHistoryView.as_view(), name="history"),
    path("session/validate/", views.BiometricSessionValidateView.as_view(), name="session-validate"),
    path("session/status/", views.BiometricSessionStatusView.as_view(), name="session-status"),
]
