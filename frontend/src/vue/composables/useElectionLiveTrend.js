import { computed, onMounted, ref, unref, watch } from "vue";
import { storeToRefs } from "pinia";
import { analyticsApi } from "@/api/analytics";
import { extractApiError } from "@/api/helpers";
import { useDashboardStore } from "@/stores/dashboard";

export function useElectionLiveTrend(electionUuidRef) {
  const dashboardStore = useDashboardStore();
  const { liveTrendSnapshots } = storeToRefs(dashboardStore);

  const data = ref(null);
  const loading = ref(false);
  const error = ref(null);
  const positionFilter = ref("all");
  const viewMode = ref("all");

  const electionUuid = computed(() => unref(electionUuidRef));

  async function fetchLiveTrend() {
    if (!electionUuid.value) return;
    loading.value = true;
    error.value = null;
    try {
      data.value = await analyticsApi.getElectionLiveTrend(electionUuid.value);
    } catch (err) {
      error.value = extractApiError(err);
    } finally {
      loading.value = false;
    }
  }

  watch(
    () => liveTrendSnapshots.value[electionUuid.value],
    (snapshot) => {
      if (snapshot) {
        data.value = snapshot;
      }
    },
  );

  watch(electionUuid, () => {
    fetchLiveTrend();
  });

  onMounted(() => {
    fetchLiveTrend();
  });

  const positions = computed(() => data.value?.positions || []);
  const summary = computed(() => data.value?.summary || {});
  const highlights = computed(() => data.value?.highlights || {});
  const charts = computed(() => data.value?.charts || {});
  const lastUpdated = computed(() => data.value?.last_updated || null);
  const hasVotes = computed(() => (summary.value.total_votes_cast || 0) > 0);

  const filteredPositions = computed(() => {
    if (positionFilter.value === "all") return positions.value;
    return positions.value.filter((position) => position.position_uuid === positionFilter.value);
  });

  const selectedPosition = computed(() => {
    if (positionFilter.value === "all") return positions.value[0] || null;
    return positions.value.find((position) => position.position_uuid === positionFilter.value) || null;
  });

  const displayCards = computed(() => {
    if (viewMode.value === "trending") {
      return highlights.value.top_trending || [];
    }
    if (viewMode.value === "closest") {
      return (highlights.value.closest_races || []).flatMap((race) => [
        { ...race.leader, position_title: race.position_title, race_margin: race.margin_percent },
        race.runner_up
          ? { ...race.runner_up, position_title: race.position_title, race_margin: race.margin_percent }
          : null,
      ]).filter(Boolean);
    }
    return (highlights.value.top_trending || []).slice(0, 4);
  });

  return {
    data,
    loading,
    error,
    positionFilter,
    viewMode,
    positions,
    summary,
    highlights,
    charts,
    lastUpdated,
    hasVotes,
    filteredPositions,
    selectedPosition,
    displayCards,
    fetchLiveTrend,
  };
}
