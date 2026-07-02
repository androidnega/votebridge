<script setup>
import { computed } from "vue";
import CandidateTrendCard from "@/components/elections/analytics/CandidateTrendCard.vue";
import BarChart from "@/components/charts/BarChart.vue";
import AreaChart from "@/components/charts/AreaChart.vue";
import { FaIcon, LoadingSkeleton, VAlert } from "@/components/ui";
import { useElectionLiveTrend } from "@/composables/useElectionLiveTrend";

const props = defineProps({
  electionUuid: { type: String, required: true },
});

const {
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
} = useElectionLiveTrend(() => props.electionUuid);

const summaryCards = computed(() => [
  {
    key: "turnout",
    label: "Turnout",
    value: `${summary.value.turnout_percent ?? 0}%`,
    hint: `${summary.value.ballots_submitted ?? 0} ballots`,
    icon: "fa-chart-line",
  },
  {
    key: "votes",
    label: "Votes cast",
    value: summary.value.total_votes_cast ?? 0,
    hint: `${summary.value.positions_active ?? 0} active positions`,
    icon: "fa-check-to-slot",
  },
  {
    key: "leader",
    label: "Current leader",
    value: selectedPosition.value?.leader?.full_name || "—",
    hint: selectedPosition.value?.position_title || "Select a position",
    icon: "fa-trophy",
    textValue: true,
  },
  {
    key: "closest",
    label: "Closest race",
    value: summary.value.closest_race?.position_title || "—",
    hint: summary.value.closest_race
      ? `${summary.value.closest_race.margin_percent}% margin`
      : "No contested races yet",
    icon: "fa-bolt",
    textValue: true,
  },
]);

const chartLabels = computed(() => selectedPosition.value?.chart?.labels || []);
const chartPercents = computed(() => selectedPosition.value?.chart?.percentages || []);
const chartCounts = computed(() => selectedPosition.value?.chart?.vote_counts || []);

const cumulativeLabels = computed(() =>
  (charts.value.cumulative_ballots || []).map((point) => point.label),
);
const cumulativeSeries = computed(() => [
  {
    name: "Cumulative votes",
    data: (charts.value.cumulative_ballots || []).map((point) => point.value),
  },
]);

function formatUpdated(value) {
  if (!value) return "—";
  return new Date(value).toLocaleTimeString(undefined, {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}
</script>

<template>
  <section class="vb-live-trend">
    <header class="vb-live-trend-header">
      <div>
        <p class="text-xs font-semibold uppercase tracking-[0.14em] text-brand-700">Live voting trend</p>
        <h2 class="mt-1 text-lg font-bold text-ink-primary">Internal race monitor</h2>
        <p class="mt-1 text-sm text-ink-secondary">
          Private admin view — candidate standings update in real time as ballots are submitted.
        </p>
      </div>
      <div class="flex flex-wrap items-center gap-2">
        <span class="rounded-full bg-surface-muted px-3 py-1 text-xs text-ink-secondary">
          Updated {{ formatUpdated(lastUpdated) }}
        </span>
        <button
          type="button"
          class="rounded-lg border border-border px-3 py-1.5 text-xs font-medium text-ink-primary hover:bg-surface-muted"
          @click="fetchLiveTrend"
        >
          <FaIcon icon="fa-rotate-right" class="mr-1.5" />
          Refresh
        </button>
      </div>
    </header>

    <VAlert v-if="error" variant="danger" class="mb-4">
      {{ error }}
    </VAlert>

    <div v-if="loading && !hasVotes" class="space-y-3">
      <LoadingSkeleton class="h-24" />
      <LoadingSkeleton class="h-48" />
    </div>

    <div
      v-else-if="!hasVotes"
      class="vb-live-trend-empty"
    >
      <FaIcon icon="fa-chart-column" class="mb-3 text-3xl text-ink-secondary" />
      <p class="text-sm font-medium text-ink-primary">No votes recorded yet for live trend.</p>
      <p class="mt-1 text-xs text-ink-secondary">Standings will appear here once the first ballot is cast.</p>
    </div>

    <template v-else>
      <div class="vb-live-trend-summary">
        <article
          v-for="card in summaryCards"
          :key="card.key"
          class="vb-live-trend-summary-card"
        >
          <div class="flex items-start justify-between gap-2">
            <div class="min-w-0">
              <p class="text-xs font-medium text-ink-secondary">{{ card.label }}</p>
              <p
                class="mt-1 truncate font-bold text-ink-primary"
                :class="card.textValue ? 'text-sm' : 'text-2xl tabular-nums'"
              >
                {{ card.value }}
              </p>
              <p class="mt-0.5 text-[11px] text-ink-secondary">{{ card.hint }}</p>
            </div>
            <FaIcon :icon="card.icon" class="text-brand-700/70" />
          </div>
        </article>
      </div>

      <div class="vb-live-trend-toolbar">
        <div class="flex flex-wrap gap-2">
          <button
            type="button"
            class="vb-live-trend-filter"
            :class="viewMode === 'all' ? 'vb-live-trend-filter--active' : ''"
            @click="viewMode = 'all'"
          >
            All positions
          </button>
          <button
            type="button"
            class="vb-live-trend-filter"
            :class="viewMode === 'trending' ? 'vb-live-trend-filter--active' : ''"
            @click="viewMode = 'trending'"
          >
            Top trending
          </button>
          <button
            type="button"
            class="vb-live-trend-filter"
            :class="viewMode === 'closest' ? 'vb-live-trend-filter--active' : ''"
            @click="viewMode = 'closest'"
          >
            Closest races
          </button>
        </div>

        <label class="flex items-center gap-2 text-sm text-ink-secondary">
          Position
          <select
            v-model="positionFilter"
            class="rounded-lg border border-border bg-white px-3 py-1.5 text-sm text-ink-primary"
          >
            <option value="all">All positions</option>
            <option
              v-for="position in positions"
              :key="position.position_uuid"
              :value="position.position_uuid"
            >
              {{ position.position_title }}
            </option>
          </select>
        </label>
      </div>

      <div v-if="viewMode !== 'all'" class="vb-live-trend-cards">
        <CandidateTrendCard
          v-for="candidate in displayCards"
          :key="`${candidate.candidate_uuid}-${candidate.position_title}`"
          :candidate="candidate"
          compact
        />
      </div>

      <div class="vb-live-trend-grid">
        <article class="vb-control-room-panel">
          <h3 class="mb-4 text-sm font-semibold text-ink-primary">
            {{ selectedPosition?.position_title || "Position" }} — live share
          </h3>
          <BarChart
            v-if="chartLabels.length"
            :labels="chartLabels"
            :values="chartPercents"
            horizontal
            percent
            height="240px"
          />
        </article>

        <article class="vb-control-room-panel">
          <h3 class="mb-4 text-sm font-semibold text-ink-primary">Vote counts</h3>
          <BarChart
            v-if="chartLabels.length"
            :labels="chartLabels"
            :values="chartCounts"
            height="240px"
          />
        </article>
      </div>

      <article v-if="cumulativeLabels.length" class="vb-control-room-panel">
        <h3 class="mb-4 text-sm font-semibold text-ink-primary">Cumulative vote accumulation</h3>
        <AreaChart
          :labels="cumulativeLabels"
          :series="cumulativeSeries"
          height="220px"
        />
      </article>

      <div class="space-y-4">
        <article
          v-for="position in filteredPositions"
          :key="position.position_uuid"
          class="vb-control-room-panel"
        >
          <div class="mb-4 flex flex-wrap items-center justify-between gap-3">
            <div>
              <h3 class="text-sm font-semibold text-ink-primary">{{ position.position_title }}</h3>
              <p class="text-xs text-ink-secondary">
                {{ position.total_votes }} votes cast
                <span v-if="position.leader">
                  · Leader: {{ position.leader.full_name }} ({{ position.leader.vote_percent }}%)
                </span>
              </p>
            </div>
            <span
              v-if="position.runner_up"
              class="rounded-full bg-amber-50 px-2.5 py-1 text-xs font-medium text-amber-800"
            >
              Margin {{ position.margin_percent }}%
            </span>
          </div>

          <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
            <CandidateTrendCard
              v-for="candidate in position.candidates"
              :key="candidate.candidate_uuid"
              :candidate="{ ...candidate, position_title: position.position_title }"
              :show-position="false"
            />
          </div>
        </article>
      </div>
    </template>
  </section>
</template>
