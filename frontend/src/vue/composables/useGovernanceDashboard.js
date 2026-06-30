import { computed, onMounted, onUnmounted, ref } from "vue";
import { useAuthStore } from "@/stores/auth";
import { useAnalyticsStore } from "@/stores/analytics";
import { useDashboardStore } from "@/stores/dashboard";
import { useOperationsStore } from "@/stores/operations";
import { useResultsStore } from "@/stores/results";
import { useSystemControlStore } from "@/stores/systemControl";
import {
  formatUptime,
  governanceChartColors,
  governanceQuickActions,
  healthLabel,
  healthToVariant,
  infrastructureLabels,
} from "@/config/governanceDashboard";
import { normalizeHealthStatus } from "@/config/systemControlHub";

function asResultList(results) {
  if (Array.isArray(results)) return results;
  if (Array.isArray(results?.items)) return results.items;
  return [];
}

function componentMap(healthPayload) {
  const components = healthPayload?.components || [];
  return Object.fromEntries(components.map((item) => [item.name, item]));
}

export function useGovernanceDashboard() {
  const authStore = useAuthStore();
  const dashboardStore = useDashboardStore();
  const operationsStore = useOperationsStore();
  const resultsStore = useResultsStore();
  const analyticsStore = useAnalyticsStore();
  const systemStore = useSystemControlStore();
  const initialLoading = ref(true);
  const now = ref(new Date());
  let clockTimer = null;

  onMounted(() => {
    clockTimer = window.setInterval(() => {
      now.value = new Date();
    }, 60_000);
  });

  onUnmounted(() => {
    if (clockTimer) window.clearInterval(clockTimer);
  });

  const overview = computed(() => dashboardStore.adminOverview || {});
  const operations = computed(() => operationsStore.overview || {});
  const analytics = computed(() => analyticsStore.overview || {});
  const systemOverview = computed(() => systemStore.overview || {});
  const environment = computed(() => systemStore.environment || {});
  const resultRows = computed(() => asResultList(resultsStore.results));

  const loading = computed(
    () => initialLoading.value || (dashboardStore.loading && !dashboardStore.adminOverview)
  );

  const currentTimeLabel = computed(() =>
    now.value.toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" })
  );

  const todayLabel = computed(() =>
    now.value.toLocaleDateString(undefined, {
      weekday: "long",
      month: "long",
      day: "numeric",
    })
  );

  const platformState = computed(() => systemOverview.value.platform_state || {});

  const platformStatusLabel = computed(() => {
    const state = platformState.value;
    if (state.primary && state.secondary) return `${state.primary} · ${state.secondary}`;
    return "Platform status unavailable";
  });

  const healthComponents = computed(() => {
    const fromSystem = componentMap(systemOverview.value.system_health);
    if (Object.keys(fromSystem).length) return fromSystem;
    return componentMap(operationsStore.health);
  });

  const infrastructureItems = computed(() => {
    const integrations = systemOverview.value.integrations || {};
    const map = healthComponents.value;

    const resolve = (key, fallback) => {
      if (key === "database") return healthToVariant(map.database?.status);
      if (key === "redis") return healthToVariant(integrations.redis?.status || map.redis?.status);
      if (key === "websockets") return healthToVariant(integrations.websockets?.status || map.websockets?.status);
      if (key === "sms") return healthToVariant(integrations.sms?.status || systemOverview.value.sms_provider);
      if (key === "email") return healthToVariant(integrations.email?.status || systemOverview.value.email_provider);
      if (key === "ussd") return healthToVariant(integrations.ussd?.status || systemOverview.value.ussd_provider);
      if (key === "storage") return healthToVariant(map.storage?.status || "unknown");
      return healthToVariant(fallback);
    };

    return infrastructureLabels.map(({ key, label }) => ({
      key,
      label,
      status: resolve(key),
    }));
  });

  const healthyServiceCount = computed(() =>
    infrastructureItems.value.filter((item) => item.status === "healthy").length
  );

  const platformHealth = computed(() =>
    normalizeHealthStatus(
      operations.value.system_health?.status ||
        systemOverview.value.system_status ||
        analytics.value?.operations_health?.status
    )
  );

  const pendingCertificationCount = computed(
    () =>
      resultsStore.certificationQueue?.length ??
      operations.value.pending_workloads?.pending_certification ??
      0
  );

  const securityAlertsOpen = computed(() => {
    const feed = dashboardStore.securityFeed?.summary;
    return feed?.open ?? overview.value.security_alerts?.open ?? 0;
  });

  const electionCounts = computed(() => {
    const status = analytics.value.election_status || operations.value.elections || {};
    return {
      open: (status.open ?? 0) + (status.paused ?? 0),
      scheduled: status.scheduled ?? 0,
      closed: status.closed ?? 0,
      draft: status.draft ?? 0,
    };
  });

  const publishedCount = computed(
    () => resultRows.value.filter((row) => row.result_status === "published").length
  );

  const certifiedCount = computed(
    () => resultRows.value.filter((row) => row.result_status === "certified").length
  );

  const governanceSummary = computed(() => [
    { label: "Open elections", value: electionCounts.value.open },
    { label: "Scheduled elections", value: electionCounts.value.scheduled },
    { label: "Closed elections", value: electionCounts.value.closed },
    { label: "Pending certification", value: pendingCertificationCount.value },
    { label: "Published", value: publishedCount.value },
  ]);

  const participationLabels = computed(
    () => analytics.value.trends?.votes_hourly?.map((point) => point.label) || []
  );

  const participationSeries = computed(() => [
    {
      name: "Votes processed",
      data: analytics.value.trends?.votes_hourly?.map((point) => point.value) || [],
      area: false,
      smooth: false,
      itemStyle: { color: governanceChartColors[0] },
      lineStyle: { width: 2 },
    },
  ]);

  const lifecycleItems = computed(() => {
    const status = analytics.value.election_status || operations.value.elections || {};
    return [
      { name: "Draft", value: status.draft ?? 0 },
      { name: "Scheduled", value: status.scheduled ?? 0 },
      { name: "Open", value: (status.open ?? 0) + (status.paused ?? 0) },
      { name: "Closed", value: status.closed ?? 0 },
      { name: "Certified", value: certifiedCount.value },
      { name: "Published", value: publishedCount.value },
    ].filter((item) => item.value > 0);
  });

  const adminActivity = computed(() => {
    const fromSystem = systemOverview.value.admin_activity || [];
    if (fromSystem.length) {
      return fromSystem.slice(0, 8).map((item) => ({
        id: item.id,
        title: item.title,
        meta: [item.actor, item.timestamp ? new Date(item.timestamp).toLocaleString() : ""]
          .filter(Boolean)
          .join(" · "),
      }));
    }
    return (dashboardStore.activityFeed || [])
      .filter((item) => !item.event_type?.includes("ballot"))
      .slice(0, 8)
      .map((item) => ({
        id: item.id || item.timestamp,
        title: item.title || item.message || item.event,
        meta: item.timestamp ? new Date(item.timestamp).toLocaleString() : "",
      }));
  });

  const pendingActions = computed(() => {
    const actions = [];
    if (pendingCertificationCount.value > 0) {
      actions.push({
        id: "certification",
        title: `${pendingCertificationCount.value} election${pendingCertificationCount.value === 1 ? "" : "s"} awaiting certification`,
        route: { name: "results", query: { filter: "certification" } },
      });
    }

    const ussdStatus = healthToVariant(
      systemOverview.value.integrations?.ussd?.status || systemOverview.value.ussd_provider
    );
    if (ussdStatus !== "healthy") {
      actions.push({
        id: "ussd",
        title: "USSD provider requires attention",
        route: "/dashboard/settings/integrations?focus=ussd",
      });
    }

    const smsStatus = healthToVariant(
      systemOverview.value.integrations?.sms?.status || systemOverview.value.sms_provider
    );
    if (smsStatus !== "healthy") {
      actions.push({
        id: "sms",
        title: "SMS gateway requires validation",
        route: "/dashboard/settings/integrations?focus=sms",
      });
    }

    if (!systemOverview.value.last_backup) {
      actions.push({
        id: "backup",
        title: "Backup overdue — no recent snapshot",
        route: "/dashboard/settings/backup",
      });
    }

    if (systemOverview.value.maintenance_status?.is_enabled) {
      actions.push({
        id: "maintenance",
        title: "Maintenance mode is active",
        route: "/dashboard/settings/maintenance",
      });
    } else if (systemOverview.value.maintenance_status?.expected_return_at) {
      actions.push({
        id: "maintenance-scheduled",
        title: "Maintenance window scheduled",
        route: "/dashboard/settings/maintenance",
      });
    }

    if (securityAlertsOpen.value > 0) {
      actions.push({
        id: "security",
        title: `${securityAlertsOpen.value} open security alert${securityAlertsOpen.value === 1 ? "" : "s"}`,
        route: { name: "reports" },
      });
    }

    return actions;
  });

  const platformInfo = computed(() => [
    { label: "Environment", value: systemOverview.value.environment || environment.value.deployment_mode || "—" },
    { label: "Version", value: systemOverview.value.application_version || "—" },
    { label: "Institution", value: systemOverview.value.institution || "—" },
    { label: "Release", value: systemOverview.value.release_channel || "—" },
    {
      label: "Last backup",
      value: systemOverview.value.last_backup
        ? new Date(systemOverview.value.last_backup).toLocaleString()
        : "None recorded",
    },
    { label: "Redis", value: environment.value.redis_status || "—" },
    { label: "Database", value: environment.value.postgresql_version || "—" },
    { label: "Application uptime", value: formatUptime(environment.value.uptime_seconds) },
    { label: "Build", value: systemOverview.value.build_number || "—" },
    { label: "Git commit", value: environment.value.git_commit || import.meta.env.VITE_GIT_COMMIT || "—" },
  ]);

  const kpiCards = computed(() => [
    {
      id: "platform-health",
      title: "Platform health",
      value: healthLabel(platformHealth.value),
      hint: `${healthyServiceCount.value} of ${infrastructureItems.value.length} services healthy`,
      healthStatus: platformHealth.value,
      clickable: true,
      route: { name: "operations" },
    },
    {
      id: "platform-state",
      title: "Current platform state",
      value: platformState.value.primary || "Unknown",
      detail: platformState.value.secondary || "",
      clickable: false,
    },
    {
      id: "pending-certification",
      title: "Pending certifications",
      value: pendingCertificationCount.value,
      hint: "Closed elections awaiting official certification",
      clickable: true,
      route: { name: "results", query: { filter: "certification" } },
    },
    {
      id: "security-alerts",
      title: "Security alerts",
      value: securityAlertsOpen.value,
      hint: "Unresolved security incidents",
      clickable: true,
      route: { name: "reports" },
    },
    {
      id: "infrastructure",
      title: "Infrastructure",
      value: healthLabel(
        healthyServiceCount.value === infrastructureItems.value.length ? "healthy" : platformHealth.value
      ),
      hint: "Database · Redis · WebSockets · USSD · SMS",
      healthStatus:
        healthyServiceCount.value === infrastructureItems.value.length ? "healthy" : platformHealth.value,
      clickable: true,
      route: "/dashboard/settings/integrations",
    },
  ]);

  async function loadDashboard() {
    initialLoading.value = true;
    try {
      const tasks = [
        dashboardStore.fetchSuperAdminDashboard(),
        resultsStore.fetchResults(),
        resultsStore.fetchQueues(),
        systemStore.fetchOverview().catch(() => {}),
        systemStore.fetchEnvironment().catch(() => {}),
      ];

      if (!operationsStore.overview) {
        tasks.push(operationsStore.fetchOverview());
      }
      if (!operationsStore.health) {
        tasks.push(operationsStore.fetchHealth().catch(() => {}));
      }
      if (!analyticsStore.overview) {
        tasks.push(analyticsStore.fetchOverview());
      }

      await Promise.allSettled(tasks);
    } finally {
      initialLoading.value = false;
    }
  }

  return {
    loading,
    error: computed(() => dashboardStore.error || systemStore.error || analyticsStore.error),
    todayLabel,
    currentTimeLabel,
    platformStatusLabel,
    platformHealth,
    kpiCards,
    governanceSummary,
    infrastructureItems,
    participationLabels,
    participationSeries,
    lifecycleItems,
    adminActivity,
    pendingActions,
    platformInfo,
    quickActions: governanceQuickActions,
    chartColors: governanceChartColors,
    loadDashboard,
  };
}
