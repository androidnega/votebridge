<script setup>
import { onMounted } from "vue";
import {
  StudentActiveElectionList,
  StudentStatCards,
  StudentWelcomeHeader,
} from "@/components/dashboard/student";
import { LoadingSkeleton, VAlert } from "@/components/ui";
import { useDashboardRealtime } from "@/composables/useDashboardRealtime";
import { useStudentVotePortal } from "@/composables/useStudentVotePortal";

useDashboardRealtime("student");

const {
  dashboardStore,
  studentName,
  portalSubtitle,
  activeElectionCount,
  votesCastCount,
  countdownText,
  portalElectionCards,
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
    <VAlert v-if="dashboardStore.error || portalError" class="mb-4" variant="error">
      {{ portalError || dashboardStore.error }}
    </VAlert>

    <LoadingSkeleton
      v-if="dashboardStore.loading && !dashboardStore.studentOverview"
      variant="card"
      :rows="4"
    />

    <template v-else>
      <StudentWelcomeHeader :student-name="studentName" :subtitle="portalSubtitle" />

      <StudentStatCards
        :active-count="activeElectionCount"
        :votes-cast="votesCastCount"
        :closes-in="countdownText"
      />

      <StudentActiveElectionList :elections="portalElectionCards" :loading="portalLoading" />
    </template>
  </div>
</template>
