import { computed, ref } from "vue";
import { storeToRefs } from "pinia";
import {
  adminQuickActionsPhase51,
  chartTimeRanges,
  dashboardChartColors,
  greetingForHour,
  isSameCalendarDay,
  sliceTrendByRange,
} from "@/config/dashboardExperience";
import {
  isElectionActivityItem,
  resolveWorkspaceRoute,
} from "@/config/adminCommandCenter";
import { useAuthStore } from "@/stores/auth";
import { useAnalyticsStore } from "@/stores/analytics";
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

function formatCountdown(election) {
  const target = resolveElectionCountdownTarget(election);
  if (!target) return "";
  const diff = new Date(target).getTime() - Date.now();
  if (diff <= 0) return "Now";
  const hours = Math.floor(diff / 3_600_000);
  const mins = Math.floor((diff % 3_600_000) / 60_000);
  return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`;
}

export function useAdminCommandCenter() {
  const authStore = useAuthStore();
  const dashboardStore = useDashboardStore();
  const electionStore = useElectionStore();
  const operationsStore = useOperationsStore();
  const resultsStore = useResultsStore();
  const analyticsStore = useAnalyticsStore();
  const chartRange = ref("today");

  const { adminOverview, adminTrends, activityFeed, isRealtimeLive, openElectionsList, scheduledElections } =
    storeToRefs(dashboardStore);

  const monitoring = computed(() => adminOverview.value?.monitoring || {});
  const primaryElection = computed(() => openElectionsList.value[0] || null);
  const primaryUuid = computed(() => electionUuid(primaryElection.value));

  const allTrackedElections = computed(() => [
    ...openElectionsList.value,
    ...(scheduledElections.value || []),
  ]);

  const electionsClosingToday = computed(() =>
    allTrackedElections.value.filter((election) =>
      isSameCalendarDay(election.end_date)
    ).length
  );

  const pendingCandidateApprovals = computed(() =>
    allTrackedElections.value.reduce((sum, election) => {
      const total = election.candidate_count ?? 0;
      const approved = election.approved_candidate_count ?? 0;
      return sum + Math.max(0, total - approved);
    }, 0)
  );

  const welcomeBanner = computed(() => {
    const election = primaryElection.value || scheduledElections.value?.[0];
    const status = election ? electionStatus(election) : "none";
    const phaseLabel = election
      ? `${(election.title || election.election_title || "Election").slice(0, 40)} · ${status}`
      : "No active election phase";
    return {
      greeting: greetingForHour(),
      name: authStore.user?.first_name || authStore.fullName?.split(" ")[0] || "",
      dateLabel: new Date().toLocaleDateString(undefined, {
        weekday: "long",
        month: "long",
        day: "numeric",
        year: "numeric",
      }),
      phaseLabel,
      phaseStatus: status === "none" ? "draft" : status,
    };
  });

  const kpiCards = computed(() => [
    {
      id: "active-elections",
      title: "Active Elections",
      value: openElectionsList.value.length,
      hint: "Open or paused elections",
      icon: "elections",
      accent: "green",
      clickable: true,
      route: "/dashboard/elections",
    },
    {
      id: "registered-voters",
      title: "Registered Voters",
      value: monitoring.value.eligible_voters ?? dashboardStore.registeredVoters,
      hint: "Eligible voters across active elections",
      icon: "profile",
      accent: "blue",
    },
    {
      id: "votes-cast",
      title: "Votes Cast",
      value: monitoring.value.voters_participated ?? dashboardStore.totalVotesCast,
      hint: "Distinct voters who have voted",
      icon: "analytics",
      accent: "blue",
      trend: (adminTrends.value.votesHourly || []).slice(-8).map((p) => p.value),
    },
    {
      id: "turnout",
      title: "Current Turnout",
      value: `${monitoring.value.turnout_percentage ?? dashboardStore.turnoutPercentage}%`,
      hint: "Live eligible voter participation",
      icon: "analytics",
      accent: "green",
      trend: (adminTrends.value.turnoutHourly || []).slice(-8).map((p) => p.value),
    },
    {
      id: "closing-today",
      title: "Elections Closing Today",
      value: electionsClosingToday.value,
      hint: electionsClosingToday.value ? "Requires close-of-poll planning" : "No elections closing today",
      icon: "tasks",
      accent: electionsClosingToday.value ? "amber" : "slate",
    },
    {
      id: "candidate-approvals",
      title: "Pending Candidate Approvals",
      value: pendingCandidateApprovals.value,
      hint: "Nominated candidates awaiting approval",
      icon: "profile",
      accent: pendingCandidateApprovals.value > 0 ? "amber" : "green",
      clickable: Boolean(primaryUuid.value),
      route: primaryUuid.value ? `/dashboard/elections/${primaryUuid.value}/candidates` : null,
    },
    {
      id: "security-alerts",
      title: "Recent Security Alerts",
      value: dashboardStore.pendingSecurityAlerts,
      hint: "Open security incidents requiring review",
      icon: "security",
      accent: dashboardStore.pendingSecurityAlerts > 0 ? "red" : "green",
      clickable: true,
      route: "/dashboard/reports",
    },
  ]);

  const votingActivityLabels = computed(() => {
    const votes = sliceTrendByRange(adminTrends.value.votesHourly || [], chartRange.value);
    const turnout = sliceTrendByRange(
      isRealtimeLive.value && adminTrends.value.turnoutLive?.length > 1
        ? adminTrends.value.turnoutLive
        : adminTrends.value.turnoutHourly || [],
      chartRange.value
    );
    const source = votes.length >= turnout.length ? votes : turnout;
    return source.map((point) => point.label);
  });

  const votingActivitySeries = computed(() => {
    const votes = sliceTrendByRange(adminTrends.value.votesHourly || [], chartRange.value);
    const turnout = sliceTrendByRange(
      isRealtimeLive.value && adminTrends.value.turnoutLive?.length > 1
        ? adminTrends.value.turnoutLive
        : adminTrends.value.turnoutHourly || [],
      chartRange.value
    );
    return [
      {
        name: "Votes Cast",
        data: votes.map((point) => point.value),
        area: true,
        smooth: true,
        itemStyle: { color: dashboardChartColors[0] },
        lineStyle: { width: 2 },
      },
      {
        name: "Turnout %",
        data: turnout.map((point) => point.value),
        area: true,
        smooth: true,
        itemStyle: { color: dashboardChartColors[1] },
        lineStyle: { width: 2 },
      },
    ];
  });

  const electionStatusItems = computed(() => {
    const status = analyticsStore.overview?.election_status || {};
    const published = (resultsStore.results || []).filter((row) => row.result_status === "published").length;
    return [
      { name: "Draft", value: status.draft ?? 0 },
      { name: "Scheduled", value: status.scheduled ?? 0 },
      { name: "Open", value: (status.open ?? 0) + (status.paused ?? 0) },
      { name: "Closed", value: status.closed ?? 0 },
      { name: "Published", value: published },
    ].filter((item) => item.value > 0);
  });

  const electionActivity = computed(() =>
    (activityFeed.value || [])
      .filter(isElectionActivityItem)
      .slice(0, 10)
      .map((item) => ({
        id: item.id || item.created_at || item.timestamp,
        title: item.title || item.message || item.event,
        meta: item.description || "",
        timestamp: item.created_at || item.timestamp,
      }))
  );

  const upcomingElections = computed(() =>
    (scheduledElections.value || []).slice(0, 5).map((election) => ({
      id: election.uuid,
      title: election.title || election.election_title,
      faculty: election.faculty_name || election.department_name || election.institution_unit || "",
      startDate: election.start_date,
      status: electionStatus(election),
      countdown: formatCountdown(election),
      route: `/dashboard/elections/${election.uuid}`,
    }))
  );

  const quickActions = computed(() =>
    adminQuickActionsPhase51.map((action) => {
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
      analyticsStore.fetchOverview().catch(() => {}),
    ]);

    if (primaryUuid.value && ["draft", "scheduled"].includes(electionStatus(primaryElection.value))) {
      await electionStore.fetchReadiness(primaryUuid.value).catch(() => {});
    }
  }

  return {
    dashboardStore,
    electionStore,
    isLive: isRealtimeLive,
    chartRange,
    chartTimeRanges,
    welcomeBanner,
    kpiCards,
    votingActivityLabels,
    votingActivitySeries,
    hasVotingActivity: computed(() => votingActivityLabels.value.length > 0),
    electionStatusItems,
    electionActivity,
    upcomingElections,
    quickActions,
    chartColors: dashboardChartColors,
    loadCommandCenter,
  };
}
