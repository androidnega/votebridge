import { computed, ref } from "vue";
import { useAuthStore } from "@/stores/auth";
import { useAnalyticsStore } from "@/stores/analytics";
import { useDashboardStore } from "@/stores/dashboard";
import { useOperationsStore } from "@/stores/operations";
import { useResultsStore } from "@/stores/results";
import { useVaultAccessQueue } from "@/composables/useVaultAccessQueue";

function greetingForHour(hour) {
  if (hour < 12) return "Good morning";
  if (hour < 17) return "Good afternoon";
  return "Good evening";
}

function asResultList(results) {
  if (Array.isArray(results)) return results;
  if (Array.isArray(results?.items)) return results.items;
  return [];
}

export function useGovernanceDashboard() {
  const authStore = useAuthStore();
  const dashboardStore = useDashboardStore();
  const operationsStore = useOperationsStore();
  const resultsStore = useResultsStore();
  const analyticsStore = useAnalyticsStore();
  const vaultQueue = useVaultAccessQueue();
  const initialLoading = ref(true);

  const overview = computed(() => dashboardStore.adminOverview || {});
  const operations = computed(() => operationsStore.overview || {});
  const analytics = computed(() => analyticsStore.overview || {});
  const monitoring = computed(() => dashboardStore.monitoringSummary || {});
  const resultRows = computed(() => asResultList(resultsStore.results));

  const loading = computed(
    () => initialLoading.value || (dashboardStore.loading && !dashboardStore.adminOverview)
  );

  const greeting = computed(() => {
    const firstName = authStore.user?.first_name || "there";
    return `${greetingForHour(new Date().getHours())}, ${firstName}`;
  });

  const todayLabel = computed(() =>
    new Date().toLocaleDateString(undefined, {
      weekday: "long",
      month: "long",
      day: "numeric",
    })
  );

  const platformHealth = computed(
    () => operations.value.system_health?.status || analytics.value?.operations_health?.status || "unknown"
  );

  const publishedCount = computed(
    () => resultRows.value.filter((row) => row.result_status === "published").length
  );

  const archivedCount = computed(
    () => resultRows.value.filter((row) => row.result_status === "archived").length
  );

  const pendingCertificationCount = computed(
    () =>
      resultsStore.certificationQueue?.length ??
      operations.value.pending_workloads?.pending_certification ??
      0
  );

  const securityAlertsToday = computed(() => {
    const feed = dashboardStore.securityFeed?.summary;
    return feed?.open ?? overview.value.security_alerts?.open ?? 0;
  });

  const fraudOpenCases = computed(
    () => overview.value.fraud_cases?.open_cases ?? operations.value.fraud_summary?.open_cases ?? 0
  );

  const failedBiometricsToday = computed(() => {
    const bio = monitoring.value.biometrics || monitoring.value.biometric_summary;
    if (bio?.failed_today != null) return bio.failed_today;
    if (bio?.failed_verifications_today != null) return bio.failed_verifications_today;
    return operations.value.pending_workloads?.pending_fraud_investigations ?? 0;
  });

  const ussdStatus = computed(() => {
    const status = operations.value.ussd_summary?.gateway_status || operations.value.ussd_summary?.status;
    return status ? String(status).replace(/_/g, " ") : "Operational";
  });

  const recentActivity = computed(() => {
    const alerts = dashboardStore.securityFeed?.alerts || [];
    const feed = dashboardStore.activityFeed || [];
    if (feed.length) {
      return feed.slice(0, 6).map((item) => ({
        id: item.id || item.timestamp,
        title: item.title || item.message || item.event,
        meta: item.timestamp ? new Date(item.timestamp).toLocaleString() : "",
      }));
    }
    return alerts.slice(0, 6).map((alert) => ({
      id: alert.alert_id || alert.uuid,
      title: alert.title || alert.alert_type,
      meta: alert.created_at ? new Date(alert.created_at).toLocaleString() : "",
    }));
  });

  const governanceCards = computed(() => [
    {
      id: "pending-certifications",
      title: "Pending certifications",
      count: pendingCertificationCount.value,
      description: "Closed elections awaiting official certification.",
      actionLabel: "View results",
      route: { name: "results", query: { filter: "certification" } },
    },
    {
      id: "published-elections",
      title: "Elections published",
      count: publishedCount.value,
      description: "Official results released to the institution.",
      actionLabel: "View results",
      route: { name: "results", query: { filter: "published" } },
    },
    {
      id: "active-elections",
      title: "Active elections",
      count: operations.value.elections?.open ?? overview.value.active_elections ?? 0,
      description: "Elections currently open or paused.",
      actionLabel: "View elections",
      route: { name: "elections" },
    },
    {
      id: "platform-health",
      title: "Platform health",
      count: platformHealth.value === "healthy" ? "Healthy" : platformHealth.value,
      description: "Core services and realtime connectivity.",
      actionLabel: "View operations",
      route: { name: "operations" },
    },
    {
      id: "security-alerts",
      title: "Security alerts",
      count: securityAlertsToday.value,
      description: "Open security alerts requiring attention.",
      actionLabel: "View details",
      route: { name: "reports" },
    },
    {
      id: "fraud-cases",
      title: "Fraud cases",
      count: fraudOpenCases.value,
      description: "Open fraud investigations across the platform.",
      actionLabel: "View summary",
      route: { name: "reports" },
    },
    {
      id: "failed-biometrics",
      title: "Failed biometrics today",
      count: failedBiometricsToday.value,
      description: "Identity verification failures recorded today.",
      actionLabel: "View",
      route: { name: "strongroom-identity" },
    },
    {
      id: "vault-requests",
      title: "Pending Strong Room requests",
      count: vaultQueue.pendingRequests.value.length,
      description: "Vault access requests awaiting governance approval.",
      actionLabel: "View requests",
      route: { name: "strong-room-requests" },
    },
  ]);

  const securityPreviews = computed(() => [
    {
      id: "security-alerts",
      title: "Security alerts",
      value: `${securityAlertsToday.value} open`,
      route: { name: "reports" },
    },
    {
      id: "fraud-cases",
      title: "Fraud cases",
      value: `${fraudOpenCases.value} open`,
      route: { name: "reports" },
    },
    {
      id: "biometrics",
      title: "Failed biometrics",
      value: `${failedBiometricsToday.value} today`,
      route: { name: "strongroom-identity" },
    },
    {
      id: "ussd",
      title: "USSD status",
      value: ussdStatus.value,
      route: { name: "reports" },
    },
  ]);

  async function loadDashboard() {
    initialLoading.value = true;
    try {
      const tasks = [
        dashboardStore.fetchSuperAdminDashboard(),
        resultsStore.fetchResults(),
        resultsStore.fetchQueues(),
      ];

      if (!operationsStore.overview) {
        tasks.push(operationsStore.fetchOverview());
      }
      if (!analyticsStore.overview) {
        tasks.push(analyticsStore.fetchOverview());
      }

      await Promise.allSettled(tasks);
      await vaultQueue.loadPendingRequests(resultRows.value).catch(() => {});
    } finally {
      initialLoading.value = false;
    }
  }

  return {
    loading,
    error: computed(() => dashboardStore.error || vaultQueue.error.value),
    greeting,
    todayLabel,
    platformHealth,
    governanceCards,
    securityPreviews,
    recentActivity,
    loadDashboard,
    pendingVaultRequests: vaultQueue.pendingRequests,
  };
}
