import { computed } from "vue";
import { useAuthStore } from "@/stores/auth";
import { useAnalyticsStore } from "@/stores/analytics";
import { useDashboardStore } from "@/stores/dashboard";
import { useOperationsStore } from "@/stores/operations";
import { useResultsStore } from "@/stores/results";
import { useDashboardRealtime } from "@/composables/useDashboardRealtime";

const ELECTION_STATUS_LABELS = {
  open: "Open",
  scheduled: "Scheduled",
  paused: "Paused",
  closed: "Closed",
  archived: "Archived",
  draft: "Draft",
};

function greetingForHour(hour) {
  if (hour < 12) return "Good morning";
  if (hour < 17) return "Good afternoon";
  return "Good evening";
}

function mapAlertToActivity(alert) {
  return {
    id: alert.alert_id || alert.id,
    title: alert.title || alert.alert_title || "Security alert",
    description: alert.description || alert.severity || "",
    created_at: alert.created_at,
  };
}

export function useSuperAdminDashboard() {
  const authStore = useAuthStore();
  const dashboardStore = useDashboardStore();
  const operationsStore = useOperationsStore();
  const resultsStore = useResultsStore();
  const analyticsStore = useAnalyticsStore();
  const realtime = useDashboardRealtime("super-admin");

  const overview = computed(() => dashboardStore.adminOverview || {});
  const operations = computed(() => operationsStore.overview || {});
  const analytics = computed(() => analyticsStore.overview || {});

  const loading = computed(
    () =>
      (dashboardStore.loading && !dashboardStore.adminOverview) ||
      (analyticsStore.loading && !analyticsStore.overview)
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
    () => operations.value.system_health?.status || analytics.value.operations_health?.status || "unknown"
  );

  const openElections = computed(
    () => operations.value.elections?.open ?? overview.value.active_elections ?? 0
  );

  const kpis = computed(() => [
    {
      id: "open-elections",
      label: "Open elections",
      value: openElections.value,
      hint: "Live or paused ballots",
    },
    {
      id: "turnout",
      label: "Overall turnout",
      value: `${overview.value.turnout_percentage ?? analytics.value.overall_turnout_percent ?? 0}%`,
      hint: `${(overview.value.total_votes_cast ?? analytics.value.total_votes ?? 0).toLocaleString()} votes cast`,
    },
    {
      id: "security",
      label: "Security alerts",
      value: overview.value.security_alerts?.open ?? 0,
      hint: `${overview.value.fraud_cases?.open_cases ?? 0} open fraud cases`,
    },
    {
      id: "certification",
      label: "Certifications waiting",
      value: resultsStore.certificationQueue?.length ?? operations.value.pending_workloads?.pending_certification ?? 0,
      hint: "Awaiting super admin review",
    },
  ]);

  const participationLabels = computed(
    () => analytics.value.trends?.votes_hourly?.map((point) => point.label) || []
  );

  const participationSeries = computed(() => [
    {
      name: "Votes",
      data: analytics.value.trends?.votes_hourly?.map((point) => point.value) || [],
      area: true,
    },
  ]);

  const electionStatusItems = computed(() => {
    const counts =
      analytics.value.election_status || operations.value.elections || {};
    return Object.entries(ELECTION_STATUS_LABELS)
      .map(([key, name]) => ({
        name,
        value: counts[key] ?? 0,
      }))
      .filter((item) => item.value > 0);
  });

  const votingChannelLabels = computed(() => {
    const ussdVotes = operations.value.ussd_summary?.completed_votes ?? 0;
    const totalVotes = overview.value.total_votes_cast ?? analytics.value.total_votes ?? 0;
    const webVotes = Math.max(0, totalVotes - ussdVotes);
    const labels = [];
    const values = [];
    if (webVotes > 0) {
      labels.push("Web");
      values.push(webVotes);
    }
    if (ussdVotes > 0) {
      labels.push("USSD");
      values.push(ussdVotes);
    }
    if (!labels.length && totalVotes > 0) {
      labels.push("Web");
      values.push(totalVotes);
    }
    return { labels, values };
  });

  const operationalCards = computed(() => [
    {
      id: "security",
      title: "Security & integrity",
      metrics: [
        { label: "Open alerts", value: overview.value.security_alerts?.open ?? 0 },
        { label: "Escalated", value: overview.value.security_alerts?.escalated ?? 0 },
        { label: "Fraud cases", value: overview.value.fraud_cases?.open_cases ?? 0 },
      ],
      route: "/dashboard/reports/security",
    },
    {
      id: "results",
      title: "Results pipeline",
      metrics: [
        {
          label: "Certification queue",
          value: resultsStore.certificationQueue?.length ?? operations.value.pending_workloads?.pending_certification ?? 0,
        },
        {
          label: "Publication queue",
          value: resultsStore.publicationQueue?.length ?? operations.value.pending_workloads?.pending_publication ?? 0,
        },
        { label: "Completed elections", value: analytics.value.completed_elections ?? 0 },
      ],
      route: "/dashboard/results/certification",
    },
    {
      id: "platform",
      title: "Platform load",
      metrics: [
        { label: "Active sessions", value: operations.value.realtime?.authenticated_sessions ?? 0 },
        { label: "SMS queue", value: operations.value.communications_summary?.pending_queue ?? 0 },
        { label: "USSD sessions", value: operations.value.ussd_summary?.active_sessions ?? 0 },
      ],
      route: "/dashboard/operations",
    },
  ]);

  const activityItems = computed(() => {
    const feed = [...dashboardStore.activityFeed];
    const alerts = dashboardStore.securityFeed?.alerts || [];
    for (const alert of alerts.slice(0, 8)) {
      feed.push(mapAlertToActivity(alert));
    }
    return feed
      .sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0))
      .slice(0, 10);
  });

  const quickActions = [
    { label: "Strong room", route: "/dashboard/strongroom" },
    { label: "Certification queue", route: "/dashboard/results/certification" },
    { label: "Publication center", route: "/dashboard/results/publication" },
    { label: "Operations center", route: "/dashboard/operations" },
    { label: "Reports", route: "/dashboard/reports" },
    { label: "System settings", route: "/dashboard/settings" },
  ];

  async function loadDashboard() {
    const tasks = [dashboardStore.fetchSuperAdminDashboard(), resultsStore.fetchQueues()];

    if (!operationsStore.overview) {
      tasks.push(operationsStore.fetchOverview());
    }
    if (!analyticsStore.overview) {
      tasks.push(analyticsStore.fetchOverview());
    }

    await Promise.allSettled(tasks);
  }

  return {
    loading,
    error: computed(() => dashboardStore.error || analyticsStore.error),
    greeting,
    todayLabel,
    platformHealth,
    openElections,
    kpis,
    participationLabels,
    participationSeries,
    electionStatusItems,
    votingChannelLabels,
    operationalCards,
    activityItems,
    quickActions,
    realtime,
    loadDashboard,
  };
}
