from django.urls import path

from apps.system.api import views

app_name = "system"

urlpatterns = [
    path("overview/", views.SystemOverviewView.as_view(), name="overview"),
    path("branding/", views.PublicBrandingView.as_view(), name="public-branding"),
    path("maintenance/", views.MaintenancePublicView.as_view(), name="maintenance-public"),
    path("step-up/challenge/", views.StepUpChallengeView.as_view(), name="step-up-challenge"),
    path("step-up/verify/", views.StepUpVerifyView.as_view(), name="step-up-verify"),
    path("institution/", views.InstitutionSettingsView.as_view(), name="institution"),
    path("settings/<str:category>/", views.SettingsCategoryView.as_view(), name="settings-category"),
    path("revisions/<str:key>/", views.SettingRevisionsView.as_view(), name="setting-revisions"),
    path("feature-flags/", views.FeatureFlagsView.as_view(), name="feature-flags"),
    path("feature-flags/<slug:key>/", views.FeatureFlagsView.as_view(), name="feature-flag-detail"),
    path("maintenance/control/", views.MaintenanceSettingsView.as_view(), name="maintenance-control"),
    path("providers/", views.ProvidersListView.as_view(), name="providers"),
    path("providers/<uuid:provider_uuid>/", views.ProviderDetailView.as_view(), name="provider-detail"),
    path("storage/", views.StorageView.as_view(), name="storage"),
    path("backups/", views.BackupListView.as_view(), name="backups"),
    path("backups/<uuid:backup_uuid>/", views.BackupDetailView.as_view(), name="backup-detail"),
    path("environment/", views.EnvironmentView.as_view(), name="environment"),
    path("license/", views.LicenseView.as_view(), name="license"),
    path("runtime/", views.RuntimeConfigView.as_view(), name="runtime"),
    path("data-reset/", views.OperationalDataResetView.as_view(), name="data-reset"),
]
