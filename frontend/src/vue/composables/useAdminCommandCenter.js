import { computed, onUnmounted, ref } from "vue";
import { storeToRefs } from "pinia";
import { branding } from "@/config/branding";
import {
  adminQuickActionsPhase51,
  chartTimeRanges,
  dashboardChartColors,
  greetingForHour,
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
import { electionsApi } from "@/api/elections";

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

function splitCountdownParts(target) {
  if (!target) return { days: 0, hours: 0, minutes: 0, seconds: 0 };
  const diff = Math.max(0, new Date(target).getTime() - Date.now());
  return {
    days: Math.floor(diff / 86_400_000),
    hours: Math.floor((diff % 86_400_000) / 3_600_000),
    minutes: Math.floor((diff % 3_600_000) / 60_000),
    seconds: Math.floor((diff % 60_000) / 1000),
  };
}

function formatElectionDateLabel(election) {
  const date = election?.start_date || election?.end_date;
  if (!date) return "Dates pending";
  return new Date(date).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function buildResultTurnoutMap(results) {
  const map = new Map();
  for (const result of results || []) {
    const uuid = result?.election_uuid;
    if (!uuid || result.turnout_percentage == null) continue;
    map.set(uuid, Number(result.turnout_percentage));
  }
  return map;
}

function latestPublishedTurnout(results) {
  const published = (results || [])
    .filter((result) => result.result_status === "published" && result.turnout_percentage != null)
    .sort((a, b) => new Date(b.published_at || 0) - new Date(a.published_at || 0));
  return published[0] ? Number(published[0].turnout_percentage) : null;
}

function formatTurnoutPercent(value) {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return "—";
  const rounded = Math.round(numeric * 10) / 10;
  return `${rounded}%`;
}

function resolveElectionTurnout(election, { liveTurnout, resultTurnoutMap }) {
  const uuid = electionUuid(election);
  const status = electionStatus(election);
  const open = ["open", "paused"].includes(status);
  const publishedTurnout = uuid ? resultTurnoutMap.get(uuid) : undefined;

  if (open) {
    const live = Number(liveTurnout) || 0;
    return {
      turnoutPercent: live,
      turnoutLabel: live > 0 ? formatTurnoutPercent(live) : "Live",
      turnoutMetricLabel: "Live turnout",
    };
  }

  if (publishedTurnout != null) {
    return {
      turnoutPercent: publishedTurnout,
      turnoutLabel: formatTurnoutPercent(publishedTurnout),
      turnoutMetricLabel: "Final turnout",
    };
  }

  return {
    turnoutPercent: 0,
    turnoutLabel: "—",
    turnoutMetricLabel: "Turnout",
  };
}

function buildPlaceholderHourlyBuckets(count = 12) {
  const buckets = [];
  const now = new Date();
  for (let index = count - 1; index >= 0; index -= 1) {
    const point = new Date(now);
    point.setHours(point.getHours() - index, 0, 0, 0);
    buckets.push({
      label: `${String(point.getHours()).padStart(2, "0")}:00`,
      value: 0,
    });
  }
  return buckets;
}

export function useAdminCommandCenter() {
  const authStore = useAuthStore();
  const dashboardStore = useDashboardStore();
  const electionStore = useElectionStore();
  const operationsStore = useOperationsStore();
  const resultsStore = useResultsStore();
  const analyticsStore = useAnalyticsStore();
  const chartRange = ref("today");
  const allElections = ref([]);
  const countdownParts = ref({ days: 0, hours: 0, minutes: 0, seconds: 0 });
  let countdownTimer = null;

  const { adminOverview, adminTrends, activityFeed, isRealtimeLive, openElectionsList, scheduledElections } =
    storeToRefs(dashboardStore);

  const monitoring = computed(() => adminOverview.value?.monitoring || {});
  const resultTurnoutMap = computed(() => buildResultTurnoutMap(resultsStore.results));
  const liveTurnout = computed(
    () => monitoring.value.turnout_percentage ?? dashboardStore.turnoutPercentage ?? 0
  );
  const benchmarkTurnout = computed(() => {
    const live = Number(liveTurnout.value) || 0;
    if (live > 0) {
      return { value: live, hint: "Eligible voters who have voted", title: "Live turnout" };
    }
    const published = latestPublishedTurnout(resultsStore.results);
    if (published != null) {
      return {
        value: published,
        hint: "Most recent published election",
        title: "Latest turnout",
      };
    }
    const avg = analyticsStore.overview?.average_turnout_percent;
    if (avg != null && Number(avg) > 0) {
      return { value: Number(avg), hint: "Average across completed elections", title: "Average turnout" };
    }
    return { value: 0, hint: "Eligible voters who have voted", title: "Live turnout" };
  });
  const primaryElection = computed(() => openElectionsList.value[0] || scheduledElections.value?.[0] || null);
  const primaryUuid = computed(() => electionUuid(primaryElection.value));
  const heroElection = computed(() => primaryElection.value || allElections.value[0] || null);
  const heroCountdownTarget = computed(() => resolveElectionCountdownTarget(heroElection.value));

  function refreshCountdown() {
    countdownParts.value = splitCountdownParts(heroCountdownTarget.value);
  }

  function startCountdownTicker() {
    refreshCountdown();
    if (countdownTimer) clearInterval(countdownTimer);
    countdownTimer = setInterval(refreshCountdown, 1000);
  }

  onUnmounted(() => {
    if (countdownTimer) clearInterval(countdownTimer);
  });

  const heroConfig = computed(() => {
    const election = heroElection.value;
    const status = election ? electionStatus(election) : "draft";
    return {
      title: election?.title || election?.election_title || "Election command center",
      subtitle: election
        ? `${greetingForHour()}, ${authStore.user?.first_name || "officer"}. Track turnout, ballot readiness, and live activity for your assigned elections.`
        : "Create or schedule an election to begin monitoring turnout and ballot activity.",
      institution: branding.institutionName,
      status,
      statusLabel: election
        ? `${(election.title || "").slice(0, 36)}${(election.title || "").length > 36 ? "…" : ""}`
        : "No active phase",
      isLive: isRealtimeLive.value && ["open", "paused"].includes(status),
      countdownLabel: election ? resolveCountdownLabel(election) : "",
      countdownParts: countdownParts.value,
      showCountdown: Boolean(heroCountdownTarget.value),
      monitorRoute: primaryUuid.value
        ? `/dashboard/elections/${primaryUuid.value}/monitor`
        : "/dashboard/elections",
    };
  });

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
      title: "Open elections",
      value: openElectionsList.value.length,
      hint: "Currently open or paused",
      icon: "elections",
      accent: "green",
      clickable: true,
      route: "/dashboard/elections",
    },
    {
      id: "turnout",
      title: benchmarkTurnout.value.title,
      value: formatTurnoutPercent(benchmarkTurnout.value.value),
      hint: benchmarkTurnout.value.hint,
      icon: "analytics",
      accent: "blue",
      clickable: Boolean(primaryUuid.value),
      route: primaryUuid.value ? `/dashboard/elections/${primaryUuid.value}/monitor` : "/dashboard/elections",
    },
    {
      id: "votes-cast",
      title: "Votes cast",
      value: monitoring.value.voters_participated ?? dashboardStore.totalVotesCast,
      hint: "Distinct voters in active elections",
      icon: "results",
      accent: "green",
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
    const buckets = source.length ? source : buildPlaceholderHourlyBuckets();
    return buckets.map((point) => point.label);
  });

  const votingActivitySeries = computed(() => {
    const votes = sliceTrendByRange(adminTrends.value.votesHourly || [], chartRange.value);
    const voteBuckets = votes.length ? votes : buildPlaceholderHourlyBuckets();
    return [
      {
        name: "Votes cast",
        data: voteBuckets.map((point) => point.value),
        area: true,
        smooth: 0.42,
        itemStyle: { color: dashboardChartColors[0] },
        lineStyle: { width: 3, cap: "round" },
      },
    ];
  });

  const isWaitingForVotes = computed(() => {
    const votes = adminTrends.value.votesHourly || [];
    const hasVotes = votes.some((point) => point.value > 0);
    const turnout = Number(liveTurnout.value) || 0;
    return !hasVotes && turnout === 0;
  });

  const electionStatusItems = computed(() => {
    const status = analyticsStore.overview?.election_status || {};
    const published = (resultsStore.results || []).filter((row) => row.result_status === "published").length;
    const items = [
      { name: "Draft", value: status.draft ?? 0 },
      { name: "Scheduled", value: status.scheduled ?? 0 },
      { name: "Open", value: (status.open ?? 0) + (status.paused ?? 0) },
      { name: "Closed", value: status.closed ?? 0 },
      { name: "Published", value: published },
    ];
    if (items.every((item) => item.value === 0)) {
      return [
        { name: "Open", value: 0 },
        { name: "Scheduled", value: 0 },
        { name: "Closed", value: 0 },
      ];
    }
    return items.filter((item) => item.value > 0);
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

  const pulseElections = computed(() => {
    const openAndScheduled = [...openElectionsList.value, ...scheduledElections.value];
    const closed = allElections.value.filter((election) =>
      ["closed", "archived"].includes(electionStatus(election))
    );
    const merged = openAndScheduled.length
      ? [...openAndScheduled, ...closed]
      : allElections.value;
    const source = merged.filter(
      (election, index, list) =>
        list.findIndex((item) => electionUuid(item) === electionUuid(election)) === index
    );
    const turnoutMap = resultTurnoutMap.value;
    const live = liveTurnout.value;

    return source.slice(0, 4).map((election) => {
      const uuid = electionUuid(election);
      const turnout = resolveElectionTurnout(election, {
        liveTurnout: uuid === primaryUuid.value ? live : 0,
        resultTurnoutMap: turnoutMap,
      });
      return {
        ...election,
        uuid,
        typeLabel: election.election_type_display || "Institutional election",
        ...turnout,
      };
    });
  });

  const electionTableRows = computed(() =>
    allElections.value.map((election) => {
      const uuid = electionUuid(election);
      const isPrimary = uuid && uuid === primaryUuid.value;
      const turnout = resolveElectionTurnout(election, {
        liveTurnout: isPrimary ? liveTurnout.value : 0,
        resultTurnoutMap: resultTurnoutMap.value,
      });
      return {
        ...election,
        uuid,
        dateLabel: formatElectionDateLabel(election),
        turnoutLabel: turnout.turnoutLabel,
      };
    })
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
      electionsApi.list({ page_size: 25 }).then((result) => {
        allElections.value = result?.items || [];
      }),
    ]);

    startCountdownTicker();

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
    heroConfig,
    kpiCards,
    pulseElections,
    electionTableRows,
    votingActivityLabels,
    votingActivitySeries,
    isWaitingForVotes,
    hasVotingActivity: computed(() => votingActivityLabels.value.length > 0),
    electionStatusItems,
    electionActivity,
    upcomingElections,
    quickActions,
    chartColors: dashboardChartColors,
    loadCommandCenter,
  };
}
