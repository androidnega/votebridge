import { createRouter, createWebHistory } from "vue-router";
import DashboardLayout from "@/layouts/DashboardLayout.vue";
import AuthLayout from "@/layouts/AuthLayout.vue";
import PublicLayout from "@/layouts/PublicLayout.vue";
import VerificationLayout from "@/layouts/VerificationLayout.vue";
import { legacyRedirectRoutes } from "@/router/legacyRedirects";
import { settingsLegacyRedirects } from "@/router/settingsLegacyRedirects";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/auth",
      component: AuthLayout,
      meta: { guest: true },
      children: [
        {
          path: "login",
          name: "auth-login",
          component: () => import("@/views/auth/LoginView.vue"),
          meta: { title: "Sign in" },
        },
        {
          path: "forgot-password",
          name: "auth-forgot-password",
          component: () => import("@/views/auth/ForgotPasswordView.vue"),
          meta: { title: "Forgot password" },
        },
        {
          path: "reset-password",
          name: "auth-reset-password",
          component: () => import("@/views/auth/ResetPasswordView.vue"),
          meta: { title: "Reset password" },
        },
        {
          path: "otp",
          name: "auth-otp",
          component: () => import("@/views/auth/OTPVerificationView.vue"),
          meta: { title: "Verify code", requiresOtp: true, guest: true },
        },
        {
          path: "biometric-verify",
          name: "auth-biometric-verify",
          component: () => import("@/views/biometrics/BiometricVerifyView.vue"),
          meta: {
            title: "Identity verification",
            requiresBiometric: true,
            guest: true,
            authBiometric: true,
          },
        },
        {
          path: "biometric-enroll",
          name: "auth-biometric-enroll",
          component: () => import("@/views/biometrics/BiometricEnrollAuthView.vue"),
          meta: {
            title: "Biometric enrollment",
            requiresEnrollment: true,
            guest: true,
            authBiometric: true,
          },
        },
        {
          path: "info/election-period",
          name: "auth-info-election-period",
          component: () => import("@/views/auth/info/AuthInfoPageView.vue"),
          meta: { title: "Election period", guest: true, infoPage: true, infoSlug: "election-period" },
        },
        {
          path: "info/voting-instructions",
          name: "auth-info-voting-instructions",
          component: () => import("@/views/auth/info/AuthInfoPageView.vue"),
          meta: { title: "Voting instructions", guest: true, infoPage: true, infoSlug: "voting-instructions" },
        },
        {
          path: "info/security",
          name: "auth-info-security",
          component: () => import("@/views/auth/info/AuthInfoPageView.vue"),
          meta: { title: "Security information", guest: true, infoPage: true, infoSlug: "security" },
        },
        {
          path: "info/help",
          name: "auth-info-help",
          component: () => import("@/views/auth/info/AuthInfoPageView.vue"),
          meta: { title: "Help & FAQ", guest: true, infoPage: true, infoSlug: "help" },
        },
      ],
    },
    {
      path: "/dashboard",
      component: DashboardLayout,
      meta: { requiresAuth: true },
      children: [
        {
          path: "",
          name: "dashboard",
          component: () => import("@/views/dashboard/DashboardHubView.vue"),
          meta: { title: "Dashboard" },
        },
        {
          path: "profile",
          name: "profile",
          component: () => import("@/views/auth/ProfileView.vue"),
          meta: { title: "Profile" },
        },
        {
          path: "profile/verify-ballot",
          name: "profile-verify-ballot",
          component: () => import("@/views/auth/VerifyBallotView.vue"),
          meta: { title: "Verify Ballot" },
        },
        {
          path: "vote-history",
          name: "student-vote-history",
          component: () => import("@/views/dashboard/StudentVoteHistoryView.vue"),
          meta: { title: "Vote history", roles: ["student", "candidate"] },
        },
        {
          path: "vote/verify/:uuid",
          name: "vote-verify",
          component: () => import("@/views/elections/VoteVerifyView.vue"),
          meta: {
            title: "Secure Voting Verification",
            roles: ["student", "candidate"],
          },
        },
        {
          path: "vote/presence/:uuid",
          name: "vote-presence",
          component: () => import("@/views/elections/VotePresenceCaptureView.vue"),
          meta: {
            title: "Confirm Your Presence",
            roles: ["student", "candidate"],
          },
        },
        {
          path: "my-elections",
          name: "student-my-elections",
          component: () => import("@/views/dashboard/StudentMyElectionsView.vue"),
          meta: { title: "My elections", roles: ["student", "candidate"] },
        },
        {
          path: "forbidden",
          name: "forbidden",
          component: () => import("@/views/errors/ForbiddenView.vue"),
          meta: { title: "Access Denied" },
        },
        {
          path: "error",
          name: "server-error",
          component: () => import("@/views/errors/ServerErrorView.vue"),
          meta: { title: "Server Error" },
        },
        {
          // Phase 62 — compatibility redirect: picks an election and forwards to workspace section.
          path: "election-management/candidates",
          name: "admin-election-candidates",
          component: () => import("@/views/elections/AdminWorkspaceRedirectView.vue"),
          props: { section: "candidates" },
          meta: { title: "Candidates", roles: ["admin"] },
        },
        {
          // Phase 62 — compatibility redirect (hidden from sidebar).
          path: "election-management/positions",
          name: "admin-election-positions",
          component: () => import("@/views/elections/AdminWorkspaceRedirectView.vue"),
          props: { section: "positions" },
          meta: { title: "Positions", roles: ["admin"] },
        },
        {
          // Phase 62 — compatibility redirect (hidden from sidebar).
          path: "election-management/eligibility",
          name: "admin-election-eligibility",
          component: () => import("@/views/elections/AdminWorkspaceRedirectView.vue"),
          props: { section: "eligibility" },
          meta: { title: "Voter Eligibility", roles: ["admin"] },
        },
        {
          // Phase 62 — compatibility redirect to election workspace monitor (hidden from sidebar).
          path: "control-room",
          name: "admin-control-room",
          component: () => import("@/views/elections/AdminControlRoomRedirectView.vue"),
          meta: { title: "Control Room", roles: ["admin"] },
        },
        {
          path: "elections/create",
          name: "election-create",
          component: () => import("@/views/elections/ElectionCreateView.vue"),
          meta: { title: "Create Election", roles: ["admin"] },
        },
        {
          path: "elections",
          name: "elections",
          component: () => import("@/views/elections/ElectionListView.vue"),
          meta: { title: "Elections" },
        },
        {
          path: "elections/:uuid",
          component: () => import("@/layouts/ElectionWorkspaceLayout.vue"),
          children: [
            {
              path: "",
              name: "election-detail",
              component: () => import("@/views/elections/ElectionRoleEntry.vue"),
              meta: { title: "Election" },
            },
            {
              path: "positions",
              name: "election-workspace-positions",
              component: () => import("@/views/elections/workspace/ElectionWorkspacePositions.vue"),
              meta: { title: "Positions", roles: ["admin"] },
            },
            {
              path: "candidates",
              name: "election-workspace-candidates",
              component: () => import("@/views/elections/workspace/ElectionWorkspaceCandidates.vue"),
              meta: { title: "Candidates", roles: ["admin"] },
            },
            {
              path: "eligibility",
              name: "election-workspace-eligibility",
              component: () => import("@/views/elections/workspace/ElectionWorkspaceEligibility.vue"),
              meta: { title: "Eligibility", roles: ["admin"] },
            },
            {
              path: "readiness",
              name: "election-workspace-readiness",
              component: () => import("@/views/elections/workspace/ElectionWorkspaceReadiness.vue"),
              meta: { title: "Readiness", roles: ["admin"] },
            },
            {
              path: "monitor",
              name: "election-workspace-monitor",
              component: () => import("@/views/elections/workspace/ElectionWorkspaceMonitor.vue"),
              meta: { title: "Control Room", roles: ["admin"] },
            },
            {
              path: "vote",
              name: "election-vote",
              component: () => import("@/views/elections/VotingWizardView.vue"),
              meta: { title: "Vote", roles: ["student", "candidate"] },
            },
            {
              path: "confirmation",
              name: "election-confirmation",
              component: () => import("@/views/elections/VoteConfirmationView.vue"),
              meta: { title: "Vote Confirmation", roles: ["student", "candidate"] },
            },
            {
              path: "committee",
              name: "election-vault-committee",
              component: () => import("@/views/strongroom/ElectionVaultCommitteeView.vue"),
              meta: { title: "Strong Room Committee", roles: ["admin", "super_admin"] },
            },
            {
              path: "vault/access",
              name: "election-vault-access",
              component: () => import("@/views/strongroom/ElectionVaultAccessView.vue"),
              meta: { title: "Vault Access", roles: ["super_admin"] },
            },
            {
              path: "vault/terminal/:sessionUuid",
              name: "election-vault-terminal",
              component: () => import("@/views/strongroom/VaultTerminalView.vue"),
              meta: {
                title: "Secure Vault Terminal",
                roles: ["super_admin"],
                requiresVaultSession: true,
              },
            },
            {
              path: "vault/evidence/:sessionUuid",
              name: "election-vault-evidence",
              component: () => import("@/views/strongroom/VaultEvidenceView.vue"),
              meta: {
                title: "Election Vault",
                roles: ["super_admin"],
                requiresVaultSession: true,
                requiresActiveVault: true,
              },
            },
          ],
        },
        {
          path: "security",
          name: "security",
          redirect: { name: "strongroom-security" },
          meta: { title: "Security", roles: ["super_admin"] },
        },
        {
          path: "security/trusted-devices",
          redirect: { name: "strongroom-trusted-devices" },
          meta: { title: "Trusted Devices", roles: ["super_admin"] },
        },
        {
          path: "fraud",
          name: "fraud",
          redirect: { name: "strongroom-fraud" },
          meta: { title: "Fraud Dashboard", roles: ["super_admin"] },
        },
        {
          path: "governance/strong-room-requests",
          name: "strong-room-requests",
          component: () => import("@/views/governance/StrongRoomRequestsView.vue"),
          meta: { title: "Strong Room Requests", roles: ["super_admin"] },
        },
        {
          path: "results",
          name: "results",
          component: () => import("@/views/results/ResultsHubView.vue"),
          meta: { title: "Results" },
        },
        {
          path: "results/certification",
          redirect: (to) => ({ name: "results", query: { ...to.query, filter: "certification" } }),
        },
        {
          path: "results/publication",
          redirect: { name: "results", query: { filter: "published" } },
        },
        {
          path: "results/archive",
          redirect: { name: "results", query: { filter: "archived" } },
        },
        {
          path: "results/:electionUuid/review",
          name: "result-review",
          component: () => import("@/views/results/ElectionReviewView.vue"),
          meta: { title: "Certification Review", roles: ["super_admin"] },
        },
        {
          path: "results/:electionUuid",
          name: "result-detail",
          component: () => import("@/views/results/ResultDetailView.vue"),
          meta: { title: "Election Results" },
        },
        {
          path: "strongroom/investigations/fraud",
          redirect: { name: "strongroom-fraud" },
        },
        {
          path: "strongroom/investigations/audit",
          redirect: { name: "strongroom-audit" },
        },
        {
          path: "strongroom/investigations/security",
          redirect: { name: "strongroom-security" },
        },
        {
          path: "strongroom/investigations/identity",
          redirect: { name: "strongroom-identity" },
        },
        {
          path: "strongroom/investigations/trusted-devices",
          redirect: { name: "strongroom-trusted-devices" },
        },
        {
          path: "strongroom/integrity",
          redirect: { name: "strongroom-integrity" },
        },
        {
          path: "strongroom/integrity/custody",
          redirect: { name: "strongroom-custody" },
        },
        {
          path: "investigations/fraud",
          name: "strongroom-fraud",
          component: () => import("@/views/fraud/FraudView.vue"),
          meta: { title: "Fraud Investigation", roles: ["super_admin"] },
        },
        {
          path: "investigations/audit",
          name: "strongroom-audit",
          component: () => import("@/views/platform/PlatformLogsView.vue"),
          meta: { title: "Audit Trail", roles: ["super_admin"] },
        },
        {
          path: "investigations/security",
          name: "strongroom-security",
          component: () => import("@/views/security/SecurityView.vue"),
          meta: { title: "Security Timeline", roles: ["super_admin"] },
        },
        {
          path: "investigations/identity",
          name: "strongroom-identity",
          component: () => import("@/views/biometrics/BiometricHistoryView.vue"),
          meta: { title: "Identity Investigations", roles: ["super_admin"] },
        },
        {
          path: "investigations/trusted-devices",
          name: "strongroom-trusted-devices",
          component: () => import("@/views/security/TrustedDevicesView.vue"),
          meta: { title: "Trusted Devices", roles: ["super_admin"] },
        },
        {
          path: "integrity/hub",
          name: "strongroom-integrity",
          component: () => import("@/views/strongroom/StrongroomDashboardView.vue"),
          meta: { title: "Election Integrity", roles: ["super_admin"] },
        },
        {
          path: "integrity/custody",
          name: "strongroom-custody",
          component: () => import("@/views/strongroom/StrongroomCustodyHubView.vue"),
          meta: { title: "Chain of Custody", roles: ["super_admin"] },
        },
        {
          path: "strongroom/:electionUuid",
          redirect: (to) => ({
            name: "election-vault-access",
            params: { uuid: to.params.electionUuid },
          }),
        },
        {
          // Phase 62 — legacy strong room root; redirects to Results (not primary nav).
          path: "strongroom",
          redirect: { name: "results" },
        },
        {
          // Phase 62 — legacy strong room catch-all; redirects to Results.
          path: "strongroom/:pathMatch(.*)*",
          redirect: { name: "results" },
        },
        {
          // Phase 62 — not in primary nav; provider config lives under Settings / Integrations.
          path: "communications",
          name: "communications",
          component: () => import("@/views/communications/CommunicationDashboardView.vue"),
          meta: { title: "Communication Center", roles: ["super_admin"] },
        },
        {
          path: "communications/logs",
          redirect: (to) => ({ name: "platform-logs", query: { ...to.query, tab: "communications" } }),
        },
        {
          path: "communications/providers",
          name: "communications-providers",
          component: () => import("@/views/communications/ProvidersView.vue"),
          meta: { title: "Providers", roles: ["super_admin"] },
        },
        {
          path: "communications/templates",
          name: "communications-templates",
          component: () => import("@/views/communications/TemplatesView.vue"),
          meta: { title: "Templates", roles: ["super_admin"] },
        },
        {
          path: "communications/test",
          name: "communications-test",
          component: () => import("@/views/communications/TestCenterView.vue"),
          meta: { title: "Test Center", roles: ["super_admin"] },
        },
        {
          path: "communications/queue",
          name: "communications-queue",
          component: () => import("@/views/communications/QueueMonitorView.vue"),
          meta: { title: "Queue Monitor", roles: ["super_admin"] },
        },
        {
          path: "notifications",
          name: "notifications",
          component: () => import("@/views/communications/NotificationCenterView.vue"),
          meta: { title: "Notification Center" },
        },
        {
          path: "ussd",
          name: "ussd",
          component: () => import("@/views/ussd/UssdDashboardView.vue"),
          meta: { title: "USSD Management", roles: ["super_admin"] },
        },
        {
          path: "ussd/sessions",
          name: "ussd-sessions",
          component: () => import("@/views/ussd/SessionMonitorView.vue"),
          meta: { title: "USSD Sessions", roles: ["super_admin"] },
        },
        {
          path: "ussd/logs",
          redirect: (to) => ({ name: "platform-logs", query: { ...to.query, tab: "ussd" } }),
        },
        {
          path: "operations",
          name: "operations",
          component: () => import("@/views/operations/OperationsOverviewView.vue"),
          meta: { title: "Operations Center", roles: ["super_admin"] },
        },
        {
          path: "operations/activity",
          name: "operations-activity",
          component: () => import("@/views/operations/OperationsActivityView.vue"),
          meta: { title: "Live Activity", roles: ["super_admin"] },
        },
        {
          path: "operations/health",
          name: "operations-health",
          component: () => import("@/views/operations/OperationsHealthView.vue"),
          meta: { title: "System Health", roles: ["super_admin"] },
        },
        {
          path: "operations/infrastructure",
          name: "operations-infrastructure",
          component: () => import("@/views/operations/OperationsInfrastructureView.vue"),
          meta: { title: "Infrastructure", roles: ["super_admin"] },
        },
        {
          path: "operations/elections",
          name: "operations-elections",
          component: () => import("@/views/operations/OperationsElectionMonitorView.vue"),
          meta: { title: "Election Monitor", roles: ["super_admin"] },
        },
        {
          path: "operations/communications",
          name: "operations-communications",
          component: () => import("@/views/operations/OperationsCommunicationsView.vue"),
          meta: { title: "Operations Communications", roles: ["super_admin"] },
        },
        {
          path: "operations/sessions",
          name: "operations-sessions",
          component: () => import("@/views/operations/OperationsSessionsView.vue"),
          meta: { title: "Users & Sessions", roles: ["super_admin"] },
        },
        {
          path: "operations/queues",
          name: "operations-queues",
          component: () => import("@/views/operations/OperationsQueuesView.vue"),
          meta: { title: "Operations Queues", roles: ["super_admin"] },
        },
        {
          path: "operations/performance",
          name: "operations-performance",
          component: () => import("@/views/operations/OperationsPerformanceView.vue"),
          meta: { title: "Performance", roles: ["super_admin"] },
        },
        {
          path: "operations/logs",
          redirect: (to) => ({ name: "platform-logs", query: { ...to.query, tab: "operations" } }),
        },
        {
          path: "platform/logs",
          name: "platform-logs",
          component: () => import("@/views/platform/PlatformLogsView.vue"),
          meta: { title: "Platform Logs", roles: ["super_admin"] },
        },
        {
          path: "system-control",
          redirect: { name: "settings" },
        },
        {
          path: "settings",
          name: "settings",
          component: () => import("@/views/system-control/SystemControlOverviewView.vue"),
          meta: { title: "Settings", roles: ["super_admin"] },
        },
        {
          path: "settings/institution",
          name: "settings-institution-hub",
          component: () => import("@/views/settings/SettingsInstitutionHubView.vue"),
          meta: { title: "Institution", roles: ["super_admin"] },
        },
        {
          path: "settings/institution/profile",
          name: "settings-institution",
          component: () => import("@/views/system-control/SystemInstitutionView.vue"),
          meta: { title: "Institution Settings", roles: ["super_admin"] },
        },
        {
          path: "settings/institution/branding",
          name: "settings-branding",
          component: () => import("@/views/system-control/SystemBrandingView.vue"),
          meta: { title: "Branding", roles: ["super_admin"] },
        },
        {
          path: "settings/integrations",
          name: "settings-integrations",
          component: () => import("@/views/system-control/SystemIntegrationsView.vue"),
          meta: { title: "Integrations", roles: ["super_admin"] },
        },
        {
          path: "settings/integrations/providers",
          name: "settings-providers",
          component: () => import("@/views/system-control/SystemProvidersView.vue"),
          meta: { title: "Communication Providers", roles: ["super_admin"] },
        },
        {
          path: "settings/integrations/ussd",
          name: "settings-ussd",
          component: () => import("@/views/system-control/SystemCategorySettingsView.vue"),
          props: { category: "ussd", title: "USSD Configuration" },
          meta: { title: "USSD Configuration", roles: ["super_admin"] },
        },
        {
          path: "settings/integrations/notifications",
          name: "settings-notifications",
          component: () => import("@/views/system-control/SystemCategorySettingsView.vue"),
          props: { category: "notifications", title: "Notification Settings" },
          meta: { title: "Notification Settings", roles: ["super_admin"] },
        },
        {
          path: "settings/integrations/channels",
          name: "settings-voting-channels",
          component: () => import("@/views/settings/VotingChannelsSettingsView.vue"),
          meta: { title: "Voting Channels", roles: ["super_admin"] },
        },
        {
          path: "settings/integrations/sms",
          name: "settings-sms",
          component: () => import("@/views/system-control/SystemSmsProvidersView.vue"),
          meta: { title: "SMS Providers", roles: ["super_admin"] },
        },
        {
          path: "settings/integrations/email",
          name: "settings-email",
          component: () => import("@/views/system-control/SystemProvidersView.vue"),
          props: { providerType: "smtp_email", title: "Email Providers" },
          meta: { title: "Email Providers", roles: ["super_admin"] },
        },
        {
          path: "settings/security",
          name: "settings-security-hub",
          component: () => import("@/views/settings/SettingsSecurityHubView.vue"),
          meta: { title: "Security", roles: ["super_admin"] },
        },
        {
          path: "settings/security/authentication",
          name: "settings-authentication",
          component: () => import("@/views/system-control/SystemCategorySettingsView.vue"),
          props: { category: "authentication", title: "Authentication", sensitive: true },
          meta: { title: "Authentication", roles: ["super_admin"] },
        },
        {
          path: "settings/security/identity-assurance",
          name: "settings-identity-assurance",
          component: () => import("@/views/system-control/SystemCategorySettingsView.vue"),
          props: { category: "identity_assurance", title: "Identity Configuration", sensitive: true },
          meta: { title: "Identity Configuration", roles: ["super_admin"] },
        },
        {
          path: "settings/security/policies",
          name: "settings-security",
          component: () => import("@/views/system-control/SystemCategorySettingsView.vue"),
          props: { category: "security", title: "Security Policies", sensitive: true },
          meta: { title: "Security Policies", roles: ["super_admin"] },
        },
        {
          path: "settings/security/election-administration",
          name: "settings-election-administration",
          component: () => import("@/views/settings/SettingsElectionAdministrationView.vue"),
          meta: { title: "Election Administration", roles: ["super_admin"] },
        },
        {
          path: "settings/security/strongroom",
          name: "settings-strongroom-config",
          component: () => import("@/views/settings/SettingsStrongroomConfigView.vue"),
          meta: { title: "Strong Room Configuration", roles: ["super_admin"] },
        },
        {
          path: "settings/security/api",
          name: "settings-api",
          component: () => import("@/views/system-control/SystemCategorySettingsView.vue"),
          props: { category: "api", title: "API & Integrations" },
          meta: { title: "API & Integrations", roles: ["super_admin"] },
        },
        {
          path: "settings/security/audit",
          name: "settings-audit",
          component: () => import("@/views/system-control/SystemCategorySettingsView.vue"),
          props: { category: "audit", title: "Audit Settings" },
          meta: { title: "Audit Settings", roles: ["super_admin"] },
        },
        {
          path: "settings/advanced",
          name: "settings-advanced-hub",
          component: () => import("@/views/settings/SettingsAdvancedHubView.vue"),
          meta: { title: "Advanced", roles: ["super_admin"] },
        },
        {
          path: "settings/advanced/platform-defaults",
          name: "settings-platform-defaults",
          component: () => import("@/views/system-control/PlatformDefaultsView.vue"),
          meta: { title: "Platform Defaults", roles: ["super_admin"] },
        },
        {
          path: "settings/advanced/feature-flags",
          name: "settings-feature-flags",
          component: () => import("@/views/system-control/SystemFeatureFlagsView.vue"),
          meta: { title: "Feature Flags", roles: ["super_admin"] },
        },
        {
          path: "settings/advanced/maintenance",
          name: "settings-maintenance",
          component: () => import("@/views/system-control/SystemMaintenanceView.vue"),
          meta: { title: "System Maintenance", roles: ["super_admin"] },
        },
        {
          path: "settings/advanced/backup",
          name: "settings-backup",
          component: () => import("@/views/system-control/SystemBackupView.vue"),
          meta: { title: "Backup & Recovery", roles: ["super_admin"] },
        },
        {
          path: "settings/advanced/system",
          name: "settings-system",
          component: () => import("@/views/settings/SettingsSystemHubView.vue"),
          meta: { title: "System Configuration", roles: ["super_admin"] },
        },
        {
          path: "settings/advanced/runtime",
          name: "settings-runtime",
          component: () => import("@/views/system-control/SystemRuntimeView.vue"),
          meta: { title: "Runtime Configuration", roles: ["super_admin"] },
        },
        {
          path: "settings/advanced/environment",
          name: "settings-environment",
          component: () => import("@/views/system-control/SystemEnvironmentView.vue"),
          meta: { title: "Environment", roles: ["super_admin"] },
        },
        {
          path: "settings/advanced/storage",
          name: "settings-storage",
          component: () => import("@/views/system-control/SystemStorageView.vue"),
          meta: { title: "Storage", roles: ["super_admin"] },
        },
        {
          path: "settings/advanced/license",
          name: "settings-license",
          component: () => import("@/views/system-control/SystemLicenseView.vue"),
          meta: { title: "License", roles: ["super_admin"] },
        },
        {
          path: "settings/advanced/about",
          name: "settings-about",
          component: () => import("@/views/system-control/SystemAboutView.vue"),
          meta: { title: "About VoteBridge", roles: ["super_admin"] },
        },
        {
          path: "settings/advanced/data-reset",
          name: "settings-data-reset",
          component: () => import("@/views/system-control/SystemDataResetView.vue"),
          meta: { title: "Operational Data Reset", roles: ["super_admin"] },
        },
        ...settingsLegacyRedirects.map(({ path, redirect }) => ({ path, redirect })),
        {
          path: "biometrics/enroll",
          name: "biometrics-enroll",
          component: () => import("@/views/biometrics/BiometricEnrollView.vue"),
          meta: { title: "Biometric Enrollment", roles: ["super_admin"] },
        },
        {
          path: "biometrics/history",
          name: "biometrics-history",
          component: () => import("@/views/biometrics/BiometricHistoryView.vue"),
          meta: { title: "Biometric History", roles: ["admin", "super_admin"] },
        },
        {
          path: "analytics",
          redirect: { name: "reports" },
        },
        {
          path: "reports",
          name: "reports",
          component: () => import("@/views/analytics/ReportsWorkspaceView.vue"),
          meta: { title: "Reports", roles: ["admin", "super_admin"] },
        },
        {
          path: "reports/participation",
          redirect: { name: "reports" },
        },
        {
          path: "reports/turnout",
          redirect: { name: "reports" },
        },
        {
          path: "reports/results",
          redirect: { name: "reports" },
        },
        {
          path: "reports/explore/students",
          redirect: { name: "reports" },
        },
        {
          path: "reports/explore/departments",
          redirect: { name: "reports" },
        },
        {
          path: "reports/explore/faculties",
          redirect: { name: "reports" },
        },
        {
          path: "reports/explore/programmes",
          redirect: { name: "reports" },
        },
        {
          path: "reports/explore/security",
          redirect: { name: "reports" },
        },
        {
          path: "reports/explore/fraud",
          redirect: { name: "reports" },
        },
        {
          path: "reports/explore/communications",
          redirect: { name: "reports" },
        },
        {
          path: "reports/explore/ussd",
          redirect: { name: "reports" },
        },
        {
          path: "reports/historical",
          redirect: { name: "reports" },
        },
        {
          path: "reports/export",
          redirect: { name: "reports" },
        },
        {
          path: "analytics/elections",
          redirect: { name: "reports" },
        },
        {
          path: "analytics/participation",
          redirect: { name: "reports" },
        },
        {
          path: "analytics/students",
          redirect: { name: "reports" },
        },
        {
          path: "analytics/departments",
          redirect: { name: "reports" },
        },
        {
          path: "analytics/faculties",
          redirect: { name: "reports" },
        },
        {
          path: "analytics/programmes",
          redirect: { name: "reports" },
        },
        {
          path: "analytics/security",
          redirect: { name: "reports" },
        },
        {
          path: "analytics/fraud",
          redirect: { name: "reports" },
        },
        {
          path: "analytics/operations",
          name: "analytics-operations",
          component: () => import("@/views/analytics/AnalyticsOperationsView.vue"),
          meta: { title: "Operations Analytics", roles: ["admin", "super_admin"] },
        },
        {
          path: "analytics/communications",
          redirect: { name: "reports" },
        },
        {
          path: "analytics/ussd",
          redirect: { name: "reports" },
        },
        {
          path: "analytics/strongroom",
          name: "analytics-strongroom",
          component: () => import("@/views/analytics/AnalyticsStrongroomView.vue"),
          meta: { title: "Strongroom Analytics", roles: ["admin", "super_admin"] },
        },
        {
          path: "analytics/historical",
          redirect: { name: "reports" },
        },
        {
          path: "analytics/reports",
          redirect: { name: "reports" },
        },
      ],
    },
    {
      path: "/",
      component: PublicLayout,
      meta: { public: true },
      children: [
        {
          path: "",
          name: "landing",
          component: () => import("@/views/public/LandingView.vue"),
          meta: { title: "Welcome", public: true },
        },
      ],
    },
    // Observer portal excluded from v1.0 — re-enable via router/observerRoutes.v2.js
    {
      path: "/maintenance",
      component: PublicLayout,
      meta: { public: true },
      children: [
        {
          path: "",
          name: "maintenance",
          component: () => import("@/views/errors/MaintenanceView.vue"),
          meta: { title: "Maintenance", public: true },
        },
      ],
    },
    {
      path: "/verify",
      component: VerificationLayout,
      meta: { public: true },
      children: [
        {
          path: "",
          name: "verify-election",
          component: () => import("@/views/strongroom/VerificationCenterView.vue"),
          meta: { title: "Verification Center", public: true },
        },
      ],
    },
    ...legacyRedirectRoutes,
    {
      path: "/:pathMatch(.*)*",
      name: "not-found",
      component: () => import("@/views/NotFoundView.vue"),
      meta: { title: "Not Found" },
    },
  ],
  scrollBehavior() {
    return { top: 0 };
  },
});

export default router;
