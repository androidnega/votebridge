<script setup>
import { computed } from "vue";
import CandidateTrendCard from "@/components/elections/analytics/CandidateTrendCard.vue";
import BarChart from "@/components/charts/BarChart.vue";
import AreaChart from "@/components/charts/AreaChart.vue";
import DonutChart from "@/components/charts/DonutChart.vue";
import { FaIcon, LoadingSkeleton, VAlert } from "@/components/ui";
import { useElectionResultsAnalytics } from "@/composables/useElectionResultsAnalytics";

const props = defineProps({
  electionUuid: { type: String, required: true },
});

const {
  loading,
  error,
  positionFilter,
  positions,
  summary,
  candidates,
  charts,
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
} = useElectionResultsAnalytics(() => props.electionUuid);

const summaryCards = computed(() => [
  {
    key: "eligible",
    label: "Eligible voters",
    value: summary.value.eligible_voters ?? 0,
    hint: "Registered roll",
    icon: "fa-users",
  },
  {
    key: "ballots",
    label: "Ballots cast",
    value: summary.value.ballots_submitted ?? 0,
    hint: `${summary.value.turnout_percent ?? 0}% turnout`,
    icon: "fa-check-to-slot",
  },
  {
    key: "positions",
    label: "Positions",
    value: summary.value.positions_total ?? 0,
    hint: `${summary.value.candidates_total ?? 0} candidates`,
    icon: "fa-list-ol",
  },
  {
    key: "closest",
    label: "Closest race",
    value: summary.value.closest_race?.position_title || "—",
    hint: summary.value.closest_race
      ? `${summary.value.closest_race.margin_percent}% margin`
      : "Single-candidate or uncontested",
    icon: "fa-bolt",
    textValue: true,
  },
  {
    key: "margin",
    label: "Biggest win margin",
    value: summary.value.biggest_win_margin?.position_title || "—",
    hint: summary.value.biggest_win_margin
      ? `${summary.value.biggest_win_margin.margin_percent}% lead`
      : "—",
    icon: "fa-trophy",
    textValue: true,
  },
  {
    key: "competitive",
    label: "Most competitive",
    value: summary.value.most_competitive_position?.position_title || "—",
    hint: "Tightest finish",
    icon: "fa-chart-line",
    textValue: true,
  },
]);

const positionChartLabels = computed(() => charts.value.votes_by_position?.labels || []);
const positionChartValues = computed(() => charts.value.votes_by_position?.values || []);
const selectedLabels = computed(() => selectedPosition.value?.chart?.labels || []);
const selectedCounts = computed(() => selectedPosition.value?.chart?.vote_counts || []);
const selectedPercents = computed(() => selectedPosition.value?.chart?.percentages || []);

const facultyBar = computed(() => {
  const rows = charts.value.turnout_by_faculty || [];
  return {
    labels: rows.map((row) => row.faculty),
    values: rows.map((row) => row.turnout_percent),
  };
});

function formatUpdated(value) {
  if (!value) return "—";
  return new Date(value).toLocaleString();
}
</script>

<template>
  <section class="vb-election-analytics">
    <header class="vb-election-analytics-header">
      <div>
        <p class="text-xs font-semibold uppercase tracking-[0.14em] text-brand-700">Election analytics</p>
        <h2 class="mt-1 text-lg font-bold text-ink-primary">Performance report</h2>
        <p class="mt-1 text-sm text-ink-secondary">
          Inspect turnout, margins, and candidate performance across every position.
        </p>
      </div>
      <div class="flex items-center gap-2">
        <span class="text-xs text-ink-secondary">Generated {{ formatUpdated(lastUpdated) }}</span>
        <button
          type="button"
          class="rounded-lg border border-border px-3 py-1.5 text-xs font-medium text-ink-primary hover:bg-surface-muted"
          @click="fetchAnalytics"
        >
          <FaIcon icon="fa-rotate-right" class="mr-1.5" />
          Refresh
        </button>
      </div>
    </header>

    <VAlert v-if="error" variant="danger" class="mb-4">
      {{ error }}
    </VAlert>

    <div v-if="loading && !positions.length" class="space-y-3">
      <LoadingSkeleton class="h-24" />
      <LoadingSkeleton class="h-64" />
    </div>

    <template v-else>
      <div class="vb-election-analytics-summary">
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
        <label class="flex items-center gap-2 text-sm text-ink-secondary">
          Position focus
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

      <div class="vb-election-analytics-grid">
        <article class="vb-control-room-panel">
          <h3 class="mb-4 text-sm font-semibold text-ink-primary">Total votes by position</h3>
          <BarChart
            v-if="positionChartLabels.length"
            :labels="positionChartLabels"
            :values="positionChartValues"
            height="280px"
          />
        </article>

        <article class="vb-control-room-panel">
          <h3 class="mb-4 text-sm font-semibold text-ink-primary">Turnout by faculty</h3>
          <BarChart
            v-if="facultyBar.labels.length"
            :labels="facultyBar.labels"
            :values="facultyBar.values"
            horizontal
            percent
            height="280px"
          />
        </article>
      </div>

      <div class="vb-election-analytics-grid">
        <article class="vb-control-room-panel">
          <h3 class="mb-4 text-sm font-semibold text-ink-primary">Cumulative ballot submissions</h3>
          <AreaChart
            v-if="cumulativeLabels.length"
            :labels="cumulativeLabels"
            :series="cumulativeSeries"
            height="240px"
          />
        </article>

        <article class="vb-control-room-panel">
          <h3 class="mb-4 text-sm font-semibold text-ink-primary">Hourly vote volume</h3>
          <AreaChart
            v-if="hourlyLabels.length"
            :labels="hourlyLabels"
            :series="hourlySeries"
            height="240px"
          />
        </article>
      </div>

      <div class="vb-election-analytics-grid">
        <article class="vb-control-room-panel">
          <h3 class="mb-4 text-sm font-semibold text-ink-primary">Participation by programme</h3>
          <DonutChart
            v-if="programmeDonut.length"
            :items="programmeDonut"
            donut
            height="280px"
          />
        </article>

        <article class="vb-control-room-panel">
          <h3 class="mb-4 text-sm font-semibold text-ink-primary">Channel split</h3>
          <DonutChart
            v-if="channelDonut.length"
            :items="channelDonut"
            donut
            height="280px"
          />
        </article>
      </div>

      <div class="vb-election-analytics-grid">
        <article class="vb-control-room-panel">
          <h3 class="mb-4 text-sm font-semibold text-ink-primary">
            {{ selectedPosition?.position_title || "Position" }} — vote counts
          </h3>
          <BarChart
            v-if="selectedLabels.length"
            :labels="selectedLabels"
            :values="selectedCounts"
            horizontal
            height="260px"
          />
        </article>

        <article class="vb-control-room-panel">
          <h3 class="mb-4 text-sm font-semibold text-ink-primary">Candidate share (%)</h3>
          <BarChart
            v-if="selectedLabels.length"
            :labels="selectedLabels"
            :values="selectedPercents"
            horizontal
            percent
            height="260px"
          />
        </article>
      </div>

      <article
        v-for="position in filteredPositions"
        :key="position.position_uuid"
        class="vb-control-room-panel"
      >
        <div class="mb-4 flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 class="text-sm font-semibold text-ink-primary">{{ position.position_title }}</h3>
            <p class="text-xs text-ink-secondary">
              Winner: {{ position.winner?.full_name || "—" }}
              <span v-if="position.runner_up">
                · Runner-up: {{ position.runner_up.full_name }} ({{ position.margin_percent }}% margin)
              </span>
            </p>
          </div>
          <span class="text-xs font-medium text-ink-secondary">{{ position.total_votes }} votes</span>
        </div>

        <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          <CandidateTrendCard
            v-for="candidate in position.candidates"
            :key="candidate.candidate_uuid"
            :candidate="{
              ...candidate,
              position_title: position.position_title,
            }"
            :show-position="false"
          />
        </div>
      </article>

      <article class="vb-control-room-panel">
        <h3 class="mb-4 text-sm font-semibold text-ink-primary">Candidate performance index</h3>
        <div class="overflow-x-auto">
          <table class="min-w-full text-left text-sm">
            <thead class="border-b border-border text-xs uppercase tracking-wide text-ink-secondary">
              <tr>
                <th class="px-3 py-2">Candidate</th>
                <th class="px-3 py-2">Position</th>
                <th class="px-3 py-2">Votes</th>
                <th class="px-3 py-2">Share</th>
                <th class="px-3 py-2">Rank</th>
                <th class="px-3 py-2">Outcome</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="row in candidates"
                :key="`${row.candidate_uuid}-${row.position_uuid}`"
                class="border-b border-border/70"
              >
                <td class="px-3 py-2.5 font-medium text-ink-primary">{{ row.full_name }}</td>
                <td class="px-3 py-2.5 text-ink-secondary">{{ row.position_title }}</td>
                <td class="px-3 py-2.5 tabular-nums">{{ row.vote_count }}</td>
                <td class="px-3 py-2.5 tabular-nums">{{ row.vote_percent }}%</td>
                <td class="px-3 py-2.5">#{{ row.rank }}</td>
                <td class="px-3 py-2.5">
                  <span
                    class="rounded-full px-2 py-0.5 text-xs font-semibold"
                    :class="row.is_winner ? 'bg-emerald-50 text-emerald-700' : 'bg-surface-muted text-ink-secondary'"
                  >
                    {{ row.is_winner ? "Winner" : "—" }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </article>
    </template>
  </section>
</template>
