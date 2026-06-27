from django.urls import path

from apps.biometrics.api import views

app_name = "biometrics"

urlpatterns = [
    path("enrollment/", views.BiometricEnrollmentView.as_view(), name="enrollment"),
    path("verification/login/", views.BiometricVerifyLoginView.as_view(), name="verify-login"),
    path("verification/step-up/", views.BiometricStepUpView.as_view(), name="verify-step-up"),
    path("challenge/", views.BiometricChallengeView.as_view(), name="challenge"),
    path("status/", views.BiometricStatusView.as_view(), name="status"),
    path("settings/", views.BiometricSettingsView.as_view(), name="settings"),
    path("history/", views.BiometricHistoryView.as_view(), name="history"),
    path("session/validate/", views.BiometricSessionValidateView.as_view(), name="session-validate"),
    path("session/status/", views.BiometricSessionStatusView.as_view(), name="session-status"),
]
