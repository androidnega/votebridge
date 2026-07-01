<script setup>
import { onMounted } from "vue";
import { StudentActiveElectionList } from "@/components/dashboard/student";
import { LoadingSkeleton, VAlert } from "@/components/ui";
import { useStudentVotePortal } from "@/composables/useStudentVotePortal";

const {
  dashboardStore,
  activeElectionCards,
  historyElectionCards,
  portalLoading,
  portalError,
  loadDashboard,
} = useStudentVotePortal();

onMounted(() => {
  loadDashboard().catch(() => {});
});
</script>

<template>
  <div>
    <header class="mb-6">
      <h1 class="text-2xl font-bold tracking-tight text-ink-primary sm:text-3xl">My elections</h1>
      <p class="mt-1.5 text-sm text-ink-secondary sm:text-base">
        Elections you are eligible to vote in this season.
      </p>
    </header>

    <VAlert v-if="dashboardStore.error || portalError" class="mb-4" variant="error">
      {{ portalError || dashboardStore.error }}
    </VAlert>

    <LoadingSkeleton
      v-if="dashboardStore.loading && !dashboardStore.studentOverview"
      variant="card"
      :rows="3"
    />

    <template v-else>
      <StudentActiveElectionList
        heading="Ready to vote"
        heading-id="ready-elections-heading"
        :elections="activeElectionCards"
        :loading="portalLoading"
        empty-message="You have no open elections waiting for your vote."
      />

      <StudentActiveElectionList
        v-if="historyElectionCards.length"
        class="mt-8"
        heading="Completed ballots"
        heading-id="completed-elections-heading"
        :elections="historyElectionCards"
        :loading="portalLoading"
        :show-open-badge="false"
      />
    </template>
  </div>
</template>
