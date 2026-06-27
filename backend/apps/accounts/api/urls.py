from django.urls import path

from apps.accounts.api.auth_views import (
    AdminLoginView,
    LogoutView,
    MFALogListView,
    OTPResendView,
    OTPVerifyView,
    SessionListView,
    SessionRevokeView,
    StudentLoginView,
    SuperAdminLoginView,
    TokenRefreshView,
    UniversalLoginView,
)
from apps.accounts.api.views import RoleViewSet, UserViewSet

app_name = "accounts"

user_list = UserViewSet.as_view({"get": "list", "post": "create"})
user_detail = UserViewSet.as_view(
    {
        "get": "retrieve",
        "put": "update",
        "patch": "partial_update",
        "delete": "destroy",
    }
)
user_status = UserViewSet.as_view({"patch": "update_status"})
user_activate = UserViewSet.as_view({"post": "activate"})
user_deactivate = UserViewSet.as_view({"post": "deactivate"})
user_verify = UserViewSet.as_view({"post": "verify"})
user_unverify = UserViewSet.as_view({"post": "unverify"})

role_list = RoleViewSet.as_view({"get": "list", "post": "create"})
role_detail = RoleViewSet.as_view(
    {
        "get": "retrieve",
        "put": "update",
        "patch": "partial_update",
        "delete": "destroy",
    }
)

urlpatterns = [
    path("auth/login/", UniversalLoginView.as_view(), name="auth-login"),
    path("auth/student/login/", StudentLoginView.as_view(), name="auth-student-login"),
    path("auth/admin/login/", AdminLoginView.as_view(), name="auth-admin-login"),
    path("auth/super-admin/login/", SuperAdminLoginView.as_view(), name="auth-super-admin-login"),
    path("auth/otp/verify/", OTPVerifyView.as_view(), name="auth-otp-verify"),
    path("auth/otp/resend/", OTPResendView.as_view(), name="auth-otp-resend"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="auth-token-refresh"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("auth/sessions/", SessionListView.as_view(), name="auth-session-list"),
    path("auth/sessions/<uuid:uuid>/revoke/", SessionRevokeView.as_view(), name="auth-session-revoke"),
    path("auth/audit-logs/", MFALogListView.as_view(), name="auth-audit-logs"),
    path("users/", user_list, name="user-list"),
    path("users/<uuid:uuid>/", user_detail, name="user-detail"),
    path("users/<uuid:uuid>/status/", user_status, name="user-status"),
    path("users/<uuid:uuid>/activate/", user_activate, name="user-activate"),
    path("users/<uuid:uuid>/deactivate/", user_deactivate, name="user-deactivate"),
    path("users/<uuid:uuid>/verify/", user_verify, name="user-verify"),
    path("users/<uuid:uuid>/unverify/", user_unverify, name="user-unverify"),
    path("roles/", role_list, name="role-list"),
    path("roles/<uuid:uuid>/", role_detail, name="role-detail"),
]
