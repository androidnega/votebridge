import { computed, onMounted, onUnmounted, ref } from "vue";
import { useAuthStore } from "@/stores/auth";
import { useAnalyticsStore } from "@/stores/analytics";
import { useDashboardStore } from "@/stores/dashboard";
import { useOperationsStore } from "@/stores/operations";
import { useResultsStore } from "@/stores/results";
import { useSystemControlStore } from "@/stores/systemControl";
import {
  dashboardChartColors,
  governanceQuickActionsPhase51,
  greetingForHour,
} from "@/config/dashboardExperience";
import {
  formatUptime,
  healthLabel,
  healthToVariant,
  infrastructureLabels,
} from "@/config/governanceDashboard";
import { settingsRoutes as r } from "@/config/settingsRoutes";
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

function isToday(value) {
  if (!value) return false;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return false;
  const today = new Date();
  return (
    date.getFullYear() === today.getFullYear()
    && date.getMonth() === today.getMonth()
    && date.getDate() === today.getDate()
  );
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

    const resolve = (key) => {
      if (key === "database") return healthToVariant(map.database?.status);
      if (key === "redis") return healthToVariant(integrations.redis?.status || map.redis?.status);
      if (key === "websockets") return healthToVariant(integrations.websockets?.status || map.websockets?.status);
      if (key === "sms") return healthToVariant(integrations.sms?.status || systemOverview.value.sms_provider);
      if (key === "email") return healthToVariant(integrations.email?.status || systemOverview.value.email_provider);
      if (key === "ussd") return healthToVariant(integrations.ussd?.status || systemOverview.value.ussd_provider);
      if (key === "storage") return healthToVariant(map.storage?.status || "unknown");
      return "unknown";
    };

    return infrastructureLabels.map(({ key, label }) => ({
      key,
      label,
      status: resolve(key),
    }));
  });

  const platformServicesChart = computed(() => {
    const counts = { Healthy: 0, Warning: 0, Offline: 0 };
    for (const item of infrastructureItems.value) {
      if (item.status === "healthy") counts.Healthy += 1;
      else if (item.status === "warning") counts.Warning += 1;
      else counts.Offline += 1;
    }
    return Object.entries(counts)
      .map(([name, value]) => ({ name, value }))
      .filter((item) => item.value > 0);
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
    return (status.open ?? 0) + (status.paused ?? 0);
  });

  const auditEventsToday = computed(() => {
    const events = systemOverview.value.admin_activity || [];
    return events.filter((item) => isToday(item.timestamp)).length;
  });

  const ussdHealthLabel = computed(() => {
    const status = healthToVariant(
      systemOverview.value.integrations?.ussd?.status || systemOverview.value.ussd_provider
    );
    return healthLabel(status);
  });

  const smsDeliveryLabel = computed(() => {
    const status = healthToVariant(
      systemOverview.value.integrations?.sms?.status || systemOverview.value.sms_provider
    );
    const fallback = systemOverview.value.integrations?.sms?.fallback_status;
    const base = healthLabel(status);
    if (fallback && fallback !== status) {
      return `${base} · Fallback ${healthLabel(healthToVariant(fallback))}`;
    }
    return base;
  });

  const onlineAdministrators = computed(() => {
    const byRole = operations.value.sessions_by_role || {};
    return (
      (byRole.admin ?? 0) +
      (byRole.super_admin ?? 0) +
      (byRole.election_officer ?? 0)
    ) || dashboardStore.activeUsersCount || 0;
  });

  const welcomeBanner = computed(() => ({
    greeting: greetingForHour(now.value.getHours()),
    name: authStore.user?.first_name || authStore.fullName?.split(" ")[0] || "",
    dateLabel: now.value.toLocaleDateString(undefined, {
      weekday: "long",
      month: "long",
      day: "numeric",
      year: "numeric",
    }),
    phaseLabel: platformStatusLabel.value,
    phaseStatus: platformState.value.has_active_election ? "open" : "draft",
  }));

  const kpiCards = computed(() => {
    const total = infrastructureItems.value.length;
    const healthy = healthyServiceCount.value;

    return [
      {
        id: "active-elections",
        title: "Active Elections",
        value: electionCounts.value,
        hint: "Open or paused elections platform-wide",
        icon: "elections",
        accent: "green",
        clickable: true,
        route: "/dashboard/elections",
      },
      {
        id: "platform-health",
        title: "Platform Health",
        value: `${healthy}/${total}`,
        detail: healthLabel(platformHealth.value),
        hint: "Core services reporting healthy",
        icon: "operations",
        accent: platformHealth.value === "healthy" ? "green" : "amber",
        clickable: true,
        route: "/dashboard/operations",
      },
      {
        id: "pending-certification",
        title: "Pending Certifications",
        value: pendingCertificationCount.value,
        hint: "Closed elections awaiting certification",
        icon: "results",
        accent: pendingCertificationCount.value > 0 ? "amber" : "green",
        clickable: true,
        route: "/dashboard/results?filter=certification",
      },
      {
        id: "security-alerts",
        title: "Security Alerts",
        value: securityAlertsOpen.value,
        hint: "Unresolved security incidents",
        icon: "security",
        accent: securityAlertsOpen.value > 0 ? "red" : "green",
        clickable: true,
        route: "/dashboard/reports",
      },
      {
        id: "audit-events",
        title: "Audit Events Today",
        value: auditEventsToday.value,
        hint: "Administrative actions recorded today",
        icon: "analytics",
        accent: "blue",
        clickable: true,
        route: { name: "platform-logs" },
      },
      {
        id: "ussd-health",
        title: "USSD Health",
        value: ussdHealthLabel.value,
        hint: "Arkesel USSD gateway status",
        icon: "communications",
        accent: ussdHealthLabel.value === "Healthy" ? "green" : "amber",
        clickable: true,
        route: `${r.integrations.hub}?focus=ussd`,
      },
      {
        id: "sms-delivery",
        title: "SMS Delivery",
        value: smsDeliveryLabel.value,
        hint: "Primary and fallback SMS gateways",
        icon: "communications",
        accent: smsDeliveryLabel.value.startsWith("Healthy") ? "green" : "amber",
        clickable: true,
        route: r.integrations.sms,
      },
      {
        id: "online-admins",
        title: "Online Administrators",
        value: onlineAdministrators.value,
        hint: "Active admin and officer sessions",
        icon: "profile",
        accent: "blue",
      },
    ];
  });

  const presentationKpiCards = computed(() =>
    kpiCards.value
      .filter((card) =>
        ["pending-certification", "active-elections", "sms-delivery"].includes(card.id)
      )
      .map((card) => {
        if (card.id === "active-elections") {
          return { ...card, clickable: false, route: undefined };
        }
        if (card.id === "sms-delivery") {
          return { ...card, route: r.integrations.sms };
        }
        return card;
      })
  );

  const participationLabels = computed(
    () => analytics.value.trends?.votes_hourly?.map((point) => point.label) || []
  );

  const participationSeries = computed(() => [
    {
      name: "Votes processed",
      data: analytics.value.trends?.votes_hourly?.map((point) => point.value) || [],
      area: true,
      smooth: true,
      itemStyle: { color: dashboardChartColors[0] },
      lineStyle: { width: 2 },
    },
  ]);

  const adminActivity = computed(() => {
    const fromSystem = systemOverview.value.admin_activity || [];
    if (fromSystem.length) {
      return fromSystem.slice(0, 10).map((item) => ({
        id: item.id,
        title: item.title,
        meta: item.actor || "",
        timestamp: item.timestamp,
      }));
    }
    return (dashboardStore.activityFeed || [])
      .filter((item) => !item.event_type?.includes("ballot"))
      .slice(0, 10)
      .map((item) => ({
        id: item.id || item.timestamp,
        title: item.title || item.message || item.event,
        meta: "",
        timestamp: item.timestamp || item.created_at,
      }));
  });

  const securityItems = computed(() => {
    const items = [];
    const summary = dashboardStore.securityFeed?.summary || {};
    const alerts = dashboardStore.securityFeed?.alerts || [];

    if (summary.failed_logins ?? summary.failed_login_attempts) {
      items.push({
        id: "failed-logins",
        title: "Failed logins",
        meta: "Authentication attempts blocked in the last 24 hours",
        count: String(summary.failed_logins ?? summary.failed_login_attempts ?? 0),
        severity: (summary.failed_logins ?? 0) > 0 ? "warning" : "healthy",
        label: String(summary.failed_logins ?? summary.failed_login_attempts ?? 0),
      });
    }

    items.push({
      id: "fraud-alerts",
      title: "Fraud alerts",
      meta: "Open fraud investigations requiring review",
      count: String(dashboardStore.openFraudCases ?? overview.value.fraud_cases?.open_cases ?? 0),
      severity: (dashboardStore.openFraudCases ?? 0) > 0 ? "warning" : "healthy",
      label: String(dashboardStore.openFraudCases ?? overview.value.fraud_cases?.open_cases ?? 0),
    });

    const strongroomPending = operations.value.pending_workloads?.pending_strongroom_requests ?? 0;
    items.push({
      id: "strongroom",
      title: "Strong Room requests",
      meta: "Vault access requests awaiting governance approval",
      count: String(strongroomPending),
      severity: strongroomPending > 0 ? "warning" : "healthy",
      label: String(strongroomPending),
    });

    items.push({
      id: "otp-failures",
      title: "OTP failures",
      meta: "Failed OTP delivery or verification attempts",
      count: String(summary.otp_failures ?? summary.failed_otp ?? 0),
      severity: (summary.otp_failures ?? summary.failed_otp ?? 0) > 0 ? "warning" : "healthy",
      label: String(summary.otp_failures ?? summary.failed_otp ?? 0),
    });

    items.push({
      id: "trusted-devices",
      title: "Trusted device changes",
      meta: "Recent trusted device enrollments or revocations",
      count: String(summary.trusted_device_changes ?? alerts.filter((a) => /trusted device/i.test(a.title || "")).length),
      severity: "info",
      label: String(summary.trusted_device_changes ?? 0),
    });

    return items;
  });

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
    currentTimeLabel: computed(() =>
      now.value.toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" })
    ),
    todayLabel: computed(() =>
      now.value.toLocaleDateString(undefined, { weekday: "long", month: "long", day: "numeric" })
    ),
    platformStatusLabel,
    welcomeBanner,
    kpiCards: presentationKpiCards,
    platformServicesChart,
    participationLabels,
    participationSeries,
    hasParticipationTrend: computed(() => participationLabels.value.length > 0),
    adminActivity,
    securityItems,
    quickActions: governanceQuickActionsPhase51,
    chartColors: dashboardChartColors,
    platformInfo: computed(() => [
      { label: "Environment", value: systemOverview.value.environment || environment.value.deployment_mode || "—" },
      { label: "Version", value: systemOverview.value.application_version || "—" },
      { label: "Uptime", value: formatUptime(environment.value.uptime_seconds) },
    ]),
    loadDashboard,
  };
}
