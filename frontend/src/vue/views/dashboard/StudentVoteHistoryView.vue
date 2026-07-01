<script setup>
import { onMounted } from "vue";
import { StudentActiveElectionList, StudentRecentActivity } from "@/components/dashboard/student";
import { LoadingSkeleton, VAlert, PageHeader } from "@/components/ui";
import { useStudentVotePortal } from "@/composables/useStudentVotePortal";

const {
  dashboardStore,
  activeElectionCards,
  historyElectionCards,
  recentActivity,
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
    <PageHeader
      title="Vote history"
      subtitle="Ballots you have submitted this season."
      :breadcrumbs="[{ label: 'Home', to: '/dashboard' }, { label: 'Vote history' }]"
    />

    <VAlert v-if="dashboardStore.error || portalError" class="mb-4" variant="error">
      {{ portalError || dashboardStore.error }}
    </VAlert>

    <LoadingSkeleton v-if="dashboardStore.loading && !dashboardStore.studentOverview" variant="card" />

    <template v-else>
      <StudentRecentActivity :items="recentActivity" />
      <StudentActiveElectionList
        class="mt-8"
        heading="Submitted ballots"
        heading-id="submitted-ballots-heading"
        :elections="historyElectionCards"
        :loading="portalLoading"
        :show-open-badge="false"
        empty-message="You have not submitted any ballots yet."
      />
    </template>
  </div>
</template>
