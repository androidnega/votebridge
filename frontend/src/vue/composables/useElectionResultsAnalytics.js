import { computed, onMounted, ref, unref, watch } from "vue";
import { analyticsApi } from "@/api/analytics";
import { extractApiError } from "@/api/helpers";

export function useElectionResultsAnalytics(electionUuidRef) {
  const data = ref(null);
  const loading = ref(false);
  const error = ref(null);
  const positionFilter = ref("all");

  const electionUuid = computed(() => unref(electionUuidRef));

  async function fetchAnalytics() {
    if (!electionUuid.value) return;
    loading.value = true;
    error.value = null;
    try {
      data.value = await analyticsApi.getElectionResultsAnalytics(electionUuid.value);
    } catch (err) {
      error.value = extractApiError(err);
    } finally {
      loading.value = false;
    }
  }

  watch(electionUuid, () => {
    fetchAnalytics();
  });

  onMounted(() => {
    fetchAnalytics();
  });

  const positions = computed(() => data.value?.positions || []);
  const summary = computed(() => data.value?.summary || {});
  const charts = computed(() => data.value?.charts || {});
  const candidates = computed(() => data.value?.candidates || []);
  const lastUpdated = computed(() => data.value?.last_updated || null);

  const filteredPositions = computed(() => {
    if (positionFilter.value === "all") return positions.value;
    return positions.value.filter((position) => position.position_uuid === positionFilter.value);
  });

  const selectedPosition = computed(() => {
    if (positionFilter.value === "all") return positions.value[0] || null;
    return positions.value.find((position) => position.position_uuid === positionFilter.value) || null;
  });

  const programmeDonut = computed(() =>
    (charts.value.turnout_by_programme || []).map((row) => ({
      name: row.label,
      value: row.participated,
    })),
  );

  const channelDonut = computed(() =>
    (charts.value.channel_split || []).map((row) => ({
      name: row.channel,
      value: row.votes,
    })),
  );

  const cumulativeSeries = computed(() => [
    {
      name: "Cumulative ballots",
      data: (charts.value.cumulative_ballots || []).map((point) => point.value),
    },
  ]);

  const cumulativeLabels = computed(() =>
    (charts.value.cumulative_ballots || []).map((point) => point.label),
  );

  const hourlySeries = computed(() => [
    {
      name: "Votes per hour",
      data: (charts.value.hourly_votes || []).map((point) => point.value),
    },
  ]);

  const hourlyLabels = computed(() =>
    (charts.value.hourly_votes || []).map((point) => point.label),
  );

  return {
    data,
    loading,
    error,
    positionFilter,
    positions,
    summary,
    charts,
    candidates,
    lastUpdated,
    filteredPositions,
    selectedPosition,
    programmeDonut,
    channelDonut,
    cumulativeSeries,
    cumulativeLabels,
    hourlySeries,
    hourlyLabels,
    fetchAnalytics,
  };
}
