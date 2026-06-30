from django.urls import path

from apps.strongroom.api import views, vault_views

app_name = "strongroom"

urlpatterns = [
    path("elections/", views.StrongroomListView.as_view(), name="strongroom-list"),
    path(
        "elections/<uuid:election_uuid>/dashboard/",
        views.StrongroomDashboardView.as_view(),
        name="strongroom-dashboard",
    ),
    path(
        "elections/<uuid:election_uuid>/custody/",
        views.CustodyTimelineView.as_view(),
        name="custody-timeline",
    ),
    path(
        "elections/<uuid:election_uuid>/verify/",
        views.VerifyIntegrityView.as_view(),
        name="verify-integrity",
    ),
    path(
        "elections/<uuid:election_uuid>/lock/",
        views.LockElectionView.as_view(),
        name="lock-election",
    ),
    path("public/verify/", views.PublicVerificationView.as_view(), name="public-verify"),
    path(
        "elections/<uuid:election_uuid>/committee/",
        vault_views.CommitteeView.as_view(),
        name="vault-committee",
    ),
    path(
        "elections/<uuid:election_uuid>/committee/submit/",
        vault_views.CommitteeSubmitView.as_view(),
        name="vault-committee-submit",
    ),
    path(
        "elections/<uuid:election_uuid>/committee/approve/",
        vault_views.CommitteeApproveView.as_view(),
        name="vault-committee-approve",
    ),
    path(
        "elections/<uuid:election_uuid>/access-requests/",
        vault_views.VaultAccessRequestListCreateView.as_view(),
        name="vault-access-requests",
    ),
    path(
        "elections/<uuid:election_uuid>/access-requests/<uuid:request_uuid>/review/",
        vault_views.VaultAccessRequestReviewView.as_view(),
        name="vault-access-request-review",
    ),
    path(
        "elections/<uuid:election_uuid>/vault-sessions/",
        vault_views.VaultSessionStartView.as_view(),
        name="vault-session-start",
    ),
    path(
        "vault-sessions/<uuid:session_uuid>/",
        vault_views.VaultSessionStatusView.as_view(),
        name="vault-session-status",
    ),
    path(
        "vault-sessions/<uuid:session_uuid>/authenticate/",
        vault_views.VaultSessionAuthenticateView.as_view(),
        name="vault-session-authenticate",
    ),
    path(
        "vault-sessions/<uuid:session_uuid>/evidence/",
        vault_views.VaultSessionDetailView.as_view(),
        name="vault-session-evidence",
    ),
    path(
        "vault-sessions/<uuid:session_uuid>/close/",
        vault_views.VaultSessionCloseView.as_view(),
        name="vault-session-close",
    ),
]
