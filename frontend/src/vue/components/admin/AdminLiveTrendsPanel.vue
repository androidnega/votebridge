<script setup>
import { computed } from "vue";
import LineChart from "@/components/charts/LineChart.vue";
import { GovernanceActivityFeed, GovernanceSectionCard } from "@/components/governance";
import { EmptyState } from "@/components/ui";
import { useAdminElectionTrends } from "@/composables/useAdminElectionTrends";

defineProps({
  showActivity: { type: Boolean, default: true },
});

const {
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
  isLive,
} = useAdminElectionTrends();

const turnoutLabels = computed(() =>
  useLiveTurnoutChart.value ? turnoutLiveLabels.value : turnoutHourlyLabels.value
);
const turnoutSeries = computed(() =>
  useLiveTurnoutChart.value ? turnoutLiveSeries.value : turnoutHourlySeries.value
);
</script>

<template>
  <section class="grid grid-cols-1 gap-6 xl:grid-cols-12" aria-label="Live election trends">
    <GovernanceSectionCard
      class="xl:col-span-4"
      title="Vote throughput"
      :subtitle="
        primaryElectionTitle
          ? `Ballots processed for ${primaryElectionTitle} — last 24 hours`
          : 'Ballots processed over the last 24 hours'
      "
    >
      <div class="mb-4 flex items-center gap-2">
        <span
          v-if="isLive"
          class="inline-flex items-center gap-1.5 rounded-input border border-success-600/20 bg-success-600/10 px-2.5 py-1 text-[0.6875rem] font-semibold uppercase tracking-wide text-success-700"
        >
          <span class="h-1.5 w-1.5 animate-pulse rounded-full bg-success-600" aria-hidden="true" />
          Live
        </span>
        <span v-else class="text-xs text-slate-500">Updates when voting is active</span>
      </div>

      <LineChart
        v-if="hasVoteTrend"
        :labels="votesLabels"
        :series="votesSeries"
        :animated="isLive"
        height="240px"
      />
      <EmptyState
        v-else
        icon="analytics"
        title="No vote activity yet"
        description="Hourly ballot counts will appear once voting begins."
      />
    </GovernanceSectionCard>

    <GovernanceSectionCard
      class="xl:col-span-4"
      title="Turnout trend"
      :subtitle="
        useLiveTurnoutChart
          ? 'Live turnout percentage as ballots arrive'
          : 'Cumulative turnout by hour while voting is open'
      "
    >
      <LineChart
        v-if="hasTurnoutTrend"
        :labels="turnoutLabels"
        :series="turnoutSeries"
        :animated="isLive"
        height="240px"
      />
      <EmptyState
        v-else
        icon="analytics"
        title="No turnout trend yet"
        description="Turnout will chart here when voters start casting ballots."
      />

      <p class="mt-4 text-xs text-slate-500">
        Aggregate participation only — candidate rankings and per-candidate totals stay hidden while
        elections are open.
      </p>
    </GovernanceSectionCard>

    <GovernanceSectionCard
      v-if="showActivity"
      class="xl:col-span-4"
      title="Live activity"
      subtitle="Ballots, alerts, and election events as they happen"
    >
      <GovernanceActivityFeed v-if="liveActivityItems.length" :items="liveActivityItems" />
      <EmptyState
        v-else
        icon="notifications"
        title="Waiting for activity"
        description="Ballot submissions and security events will stream here in real time."
      />
    </GovernanceSectionCard>
  </section>
</template>
