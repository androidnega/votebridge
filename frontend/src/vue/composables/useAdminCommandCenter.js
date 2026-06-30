import { computed } from "vue";
import { storeToRefs } from "pinia";
import {
  commandChartColors,
  commandQuickActions,
  electionLifecycleStages,
  isElectionActivityItem,
  resolveLifecycleStage,
  resolveWorkspaceRoute,
} from "@/config/adminCommandCenter";
import { useDashboardStore } from "@/stores/dashboard";
import { useElectionStore } from "@/stores/election";
import { useOperationsStore } from "@/stores/operations";
import { useResultsStore } from "@/stores/results";
import {
  resolveCountdownLabel,
  resolveElectionCountdownTarget,
} from "@/composables/useElectionCountdown";

function electionUuid(election) {
  return election?.uuid || election?.election_uuid || null;
}

function electionStatus(election) {
  return election?.status || election?.election_status || "draft";
}

function channelHealth(enabled, issueCount) {
  if (!enabled) return { label: "Off", tone: "neutral" };
  if (issueCount > 0) return { label: "Degraded", tone: "warning" };
  return { label: "Healthy", tone: "success" };
}

export function useAdminCommandCenter() {
  const dashboardStore = useDashboardStore();
  const electionStore = useElectionStore();
  const operationsStore = useOperationsStore();
  const resultsStore = useResultsStore();

  const { adminOverview, adminTrends, activityFeed, isRealtimeLive, openElectionsList, scheduledElections } =
    storeToRefs(dashboardStore);

  const monitoring = computed(() => adminOverview.value?.monitoring || {});
  const primaryElection = computed(() => openElectionsList.value[0] || null);
  const primaryUuid = computed(() => electionUuid(primaryElection.value));

  const monitorByElection = computed(() => {
    const map = new Map();
    for (const row of operationsStore.elections || []) {
      map.set(row.election_uuid, row);
    }
    return map;
  });

  const primaryResult = computed(() => {
    if (!primaryUuid.value) return null;
    return (resultsStore.results || []).find((row) => row.election_uuid === primaryUuid.value);
  });

  const pendingTasks = computed(() => {
    let count = 0;
    const election = primaryElection.value;
    if (!election) return 0;

    const status = electionStatus(election);
    if (["draft", "scheduled"].includes(status)) {
      if (electionStore.readinessReport && !electionStore.readinessReport.is_ready) {
        count += electionStore.readinessReport.blocking_issues?.length || 1;
      } else if (!electionStore.readinessReport) {
        count += 1;
      }
    }
    if (status === "paused") count += 1;
    if ((monitoring.value.fraud_alerts ?? 0) > 0) count += monitoring.value.fraud_alerts;
    if ((monitoring.value.security_alerts ?? 0) > 0) count += monitoring.value.security_alerts;
    return count;
  });

  const kpiCards = computed(() => {
    const election = primaryElection.value;
    const status = electionStatus(election);
    const countdownTarget = resolveElectionCountdownTarget(election);
    const countdownLabel = resolveCountdownLabel(election);
    let countdownValue = "—";
    if (countdownTarget) {
      const diff = new Date(countdownTarget).getTime() - Date.now();
      if (diff <= 0) {
        countdownValue = status === "scheduled" ? "Opening window" : "Closing window";
      } else {
        const hours = Math.floor(diff / 3_600_000);
        const mins = Math.floor((diff % 3_600_000) / 60_000);
        countdownValue = hours > 0 ? `${hours}h ${mins}m` : `${mins}m`;
      }
    }

    return [
      {
        id: "active-elections",
        title: "Active Elections",
        value: openElectionsList.value.length,
        hint: "Open or paused elections",
        healthStatus: openElectionsList.value.length > 0 ? "healthy" : "unknown",
      },
      {
        id: "turnout",
        title: "Turnout",
        value: `${monitoring.value.turnout_percentage ?? dashboardStore.turnoutPercentage}%`,
        hint: "Live eligible voter participation",
        healthStatus: (monitoring.value.turnout_percentage ?? 0) > 0 ? "healthy" : "unknown",
      },
      {
        id: "votes-eligible",
        title: "Votes Cast / Eligible",
        value: `${monitoring.value.voters_participated ?? 0} / ${monitoring.value.eligible_voters ?? dashboardStore.registeredVoters}`,
        hint: "Distinct voters who have voted",
        healthStatus: "unknown",
      },
      {
        id: "pending-tasks",
        title: "Pending Operational Tasks",
        value: pendingTasks.value,
        hint: pendingTasks.value ? "Requires election officer attention" : "No outstanding tasks",
        healthStatus: pendingTasks.value > 0 ? "attention" : "healthy",
      },
      {
        id: "election-status",
        title: "Current Election Status",
        value: status.charAt(0).toUpperCase() + status.slice(1),
        detail: countdownValue,
        hint: countdownLabel,
        healthStatus: status === "open" ? "healthy" : status === "paused" ? "attention" : "unknown",
      },
    ];
  });

  const activeElectionCards = computed(() =>
    openElectionsList.value.map((election) => {
      const uuid = electionUuid(election);
      const snapshot = monitorByElection.value.get(uuid) || {};
      const turnout = snapshot.turnout_percentage ?? (uuid === primaryUuid.value ? monitoring.value.turnout_percentage : null);
      return {
        election,
        uuid,
        status: electionStatus(election),
        turnout: turnout ?? 0,
        countdownTarget: resolveElectionCountdownTarget(election),
        countdownLabel: resolveCountdownLabel(election),
        monitorRoute: uuid ? `/dashboard/elections/${uuid}/monitor` : null,
      };
    })
  );

  const showReadiness = computed(() => {
    const election = primaryElection.value;
    if (!election) return false;
    return ["draft", "scheduled"].includes(electionStatus(election));
  });

  const turnoutLabels = computed(() => {
    const live = adminTrends.value.turnoutLive || [];
    const hourly = adminTrends.value.turnoutHourly || [];
    const useLive = live.length > 1 && isRealtimeLive.value;
    return (useLive ? live : hourly).map((point) => point.label);
  });

  const turnoutSeries = computed(() => {
    const live = adminTrends.value.turnoutLive || [];
    const hourly = adminTrends.value.turnoutHourly || [];
    const useLive = live.length > 1 && isRealtimeLive.value;
    const points = useLive ? live : hourly;
    return [
      {
        name: "Turnout %",
        data: points.map((point) => point.value),
        area: true,
        smooth: true,
        itemStyle: { color: commandChartColors[0] },
        lineStyle: { width: 2 },
      },
    ];
  });

  const channelDistribution = computed(() => {
    const web = monitoring.value.web_votes ?? 0;
    const ussd = monitoring.value.ussd_votes ?? 0;
    if (!web && !ussd) return [];
    return [
      { name: "Web", value: web },
      { name: "USSD", value: ussd },
    ];
  });

  const liveMonitoringItems = computed(() => {
    const channels = monitoring.value.voting_channels || {};
    const failed = monitoring.value.failed_sessions ?? 0;
    const duplicateAttempts = (activityFeed.value || []).filter(
      (item) => /duplicate/i.test(item.title || "") || /duplicate/i.test(item.description || "")
    ).length;

    return [
      {
        id: "sessions",
        label: "Active voting sessions",
        value: monitoring.value.active_sessions ?? 0,
        tone: "default",
      },
      {
        id: "web-health",
        label: "Web channel health",
        value: channelHealth(channels.web_enabled, 0).label,
        tone: channelHealth(channels.web_enabled, 0).tone,
      },
      {
        id: "ussd-health",
        label: "USSD channel health",
        value: channelHealth(channels.ussd_enabled, failed).label,
        tone: channelHealth(channels.ussd_enabled, failed).tone,
      },
      {
        id: "failed-sessions",
        label: "Failed sessions",
        value: failed,
        tone: failed > 0 ? "danger" : "success",
      },
      {
        id: "fraud-alerts",
        label: "Fraud alerts",
        value: monitoring.value.fraud_alerts ?? dashboardStore.openFraudCases,
        tone: (monitoring.value.fraud_alerts ?? 0) > 0 ? "warning" : "success",
      },
      {
        id: "duplicate-votes",
        label: "Duplicate vote attempts",
        value: duplicateAttempts,
        tone: duplicateAttempts > 0 ? "danger" : "success",
      },
    ];
  });

  const lifecycleStage = computed(() =>
    resolveLifecycleStage(primaryElection.value, primaryResult.value)
  );

  const electionActivity = computed(() =>
    (activityFeed.value || [])
      .filter(isElectionActivityItem)
      .slice(0, 8)
      .map((item) => ({
        id: item.id || item.created_at || item.timestamp,
        title: item.title || item.message || item.event,
        meta: item.description || (item.created_at ? new Date(item.created_at).toLocaleString() : ""),
      }))
  );

  const upcomingElections = computed(() =>
    (scheduledElections.value || []).slice(0, 5).map((election) => ({
      id: election.uuid,
      title: election.title || election.election_title,
      startDate: election.start_date,
      status: electionStatus(election),
      route: `/dashboard/elections/${election.uuid}`,
    }))
  );

  const quickActions = computed(() =>
    commandQuickActions.map((action) => {
      if (action.route) return action;
      const route = resolveWorkspaceRoute(primaryUuid.value, action.routeKey);
      return { ...action, route };
    })
  );

  async function loadCommandCenter() {
    await Promise.allSettled([
      dashboardStore.fetchAdminDashboard(),
      operationsStore.fetchElectionMonitor(),
      resultsStore.fetchResults(),
    ]);

    if (primaryUuid.value && showReadiness.value) {
      await electionStore.fetchReadiness(primaryUuid.value).catch(() => {});
    }
  }

  return {
    dashboardStore,
    electionStore,
    isLive: isRealtimeLive,
    primaryElection,
    primaryUuid,
    kpiCards,
    activeElectionCards,
    showReadiness,
    turnoutLabels,
    turnoutSeries,
    hasTurnoutTrend: computed(() => turnoutLabels.value.length > 0),
    channelDistribution,
    liveMonitoringItems,
    lifecycleStages: electionLifecycleStages,
    lifecycleStage,
    electionActivity,
    upcomingElections,
    quickActions,
    chartColors: commandChartColors,
    loadCommandCenter,
  };
}
