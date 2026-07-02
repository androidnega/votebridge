<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";
import ElectionStatusBadge from "@/components/voting/ElectionStatusBadge.vue";
import ElectionResultsAnalyticsDashboard from "@/components/elections/analytics/ElectionResultsAnalyticsDashboard.vue";
import { useElectionStore } from "@/stores/election";

const route = useRoute();
const electionStore = useElectionStore();

const electionUuid = computed(() => route.params.uuid);
const election = computed(() => electionStore.currentElection || {});
</script>

<template>
  <div class="vb-control-room">
    <header class="vb-control-room-header">
      <div class="min-w-0 flex-1">
        <p class="text-xs font-semibold uppercase tracking-[0.16em] text-brand-700">Analytics workspace</p>
        <div class="mt-2 flex flex-wrap items-center gap-3">
          <h1 class="text-2xl font-bold tracking-tight text-ink-primary sm:text-3xl">
            {{ election.title || "Election analytics" }}
          </h1>
          <ElectionStatusBadge :status="election.status" size="sm" />
        </div>
        <p class="mt-2 max-w-2xl text-sm text-ink-secondary">
          Internal reporting for closed elections — turnout trends, margins, and candidate performance.
        </p>
      </div>
    </header>

    <ElectionResultsAnalyticsDashboard :election-uuid="electionUuid" />
  </div>
</template>
