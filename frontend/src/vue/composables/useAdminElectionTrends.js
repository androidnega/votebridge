import { computed } from "vue";
import { storeToRefs } from "pinia";
import { adminChartColors } from "@/config/adminWorkspace";
import { useDashboardStore } from "@/stores/dashboard";

export function useAdminElectionTrends() {
  const dashboardStore = useDashboardStore();
  const { adminTrends, activityFeed, isRealtimeLive } = storeToRefs(dashboardStore);

  const primaryElectionTitle = computed(
    () => dashboardStore.adminOverview?.primary_election?.title || null
  );

  const votesLabels = computed(() => adminTrends.value.votesHourly.map((point) => point.label));

  const votesSeries = computed(() => [
    {
      name: "Ballots processed",
      data: adminTrends.value.votesHourly.map((point) => point.value),
      area: true,
      smooth: true,
      itemStyle: { color: adminChartColors[0] },
      lineStyle: { width: 2 },
    },
  ]);

  const turnoutHourlyLabels = computed(() =>
    adminTrends.value.turnoutHourly.map((point) => point.label)
  );

  const turnoutHourlySeries = computed(() => [
    {
      name: "Turnout %",
      data: adminTrends.value.turnoutHourly.map((point) => point.value),
      area: false,
      smooth: true,
      itemStyle: { color: adminChartColors[1] },
      lineStyle: { width: 2 },
    },
  ]);

  const turnoutLiveLabels = computed(() => adminTrends.value.turnoutLive.map((point) => point.label));

  const turnoutLiveSeries = computed(() => [
    {
      name: "Live turnout %",
      data: adminTrends.value.turnoutLive.map((point) => point.value),
      area: true,
      smooth: true,
      itemStyle: { color: adminChartColors[2] },
      lineStyle: { width: 2 },
    },
  ]);

  const hasVoteTrend = computed(() => votesLabels.value.length > 0);
  const hasTurnoutTrend = computed(
    () => turnoutHourlyLabels.value.length > 0 || turnoutLiveLabels.value.length > 1
  );

  const liveActivityItems = computed(() =>
    (activityFeed.value || []).slice(0, 8).map((item) => ({
      id: item.id || item.created_at || item.timestamp,
      title: item.title || item.message || item.event,
      meta: item.description || (item.created_at ? new Date(item.created_at).toLocaleString() : ""),
    }))
  );

  const useLiveTurnoutChart = computed(
    () => turnoutLiveLabels.value.length > 1 && isRealtimeLive.value
  );

  return {
    primaryElectionTitle,
    votesLabels,
    votesSeries,
    turnoutHourlyLabels,
    turnoutHourlySeries,
    turnoutLiveLabels,
    turnoutLiveSeries,
    hasVoteTrend,
    hasTurnoutTrend,
    useLiveTurnoutChart,
    liveActivityItems,
    isLive: isRealtimeLive,
    chartColors: adminChartColors,
  };
}
