<script setup>
import { computed, onMounted, ref } from "vue";
import {
  StudentCandidatePreview,
  StudentCandidateProfileModal,
  StudentCountdownCard,
  StudentDashboardNotifications,
  StudentElectionSummaryCard,
  StudentVoteHero,
  StudentVotingStatusCard,
} from "@/components/dashboard/student";
import { LoadingSkeleton, VAlert } from "@/components/ui";
import { useDashboardRealtime } from "@/composables/useDashboardRealtime";
import { useStudentVotePortal } from "@/composables/useStudentVotePortal";

useDashboardRealtime("student");

const selectedCandidate = ref(null);

const {
  dashboardStore,
  greeting,
  studentName,
  hasActiveElection,
  electionTitle,
  electionStatus,
  electionDetails,
  candidateGroups,
  notifications,
  countdown,
  countdownLabel,
  hasVoted,
  canVoteNow,
  voteRoute,
  portalLoading,
  portalError,
  formatDateTime,
  loadDashboard,
} = useStudentVotePortal();

const countdownText = computed(() => {
  const { days, hours, minutes, seconds, expired } = countdown.value;
  if (expired) return "Now";
  if (days > 0) return `${days}d ${hours}h ${minutes}m`;
  if (hours > 0) return `${hours}h ${minutes}m ${seconds}s`;
  return `${minutes}m ${seconds}s`;
});

onMounted(() => {
  loadDashboard().catch(() => {});
});
</script>

<template>
  <div class="mx-auto max-w-3xl space-y-6 pb-10 pt-2">
    <StudentVoteHero
      :greeting="greeting"
      :student-name="studentName"
      :election-title="electionTitle"
      :election-status="electionStatus"
      :countdown-label="countdownLabel"
      :countdown-text="countdownText"
      :can-vote="canVoteNow"
      :vote-route="voteRoute"
      :has-active-election="hasActiveElection"
    />

    <VAlert v-if="dashboardStore.error || portalError" variant="error">
      {{ portalError || dashboardStore.error }}
    </VAlert>

    <LoadingSkeleton
      v-if="dashboardStore.loading && !dashboardStore.studentOverview"
      variant="card"
      :rows="4"
    />

    <template v-else-if="hasActiveElection">
      <StudentElectionSummaryCard
        :title="electionTitle"
        :status="electionStatus"
        :start-date="electionDetails?.start_date"
        :end-date="electionDetails?.end_date"
        :format-date-time="formatDateTime"
        :can-vote="canVoteNow"
        :vote-route="voteRoute"
      />

      <StudentCountdownCard
        :label="countdownLabel"
        :days="countdown.days"
        :hours="countdown.hours"
        :minutes="countdown.minutes"
        :expired="countdown.expired"
      />

      <StudentVotingStatusCard :has-voted="hasVoted" />

      <StudentCandidatePreview
        :groups="candidateGroups"
        :loading="portalLoading"
        @select-candidate="selectedCandidate = $event"
      />

      <StudentDashboardNotifications :items="notifications" />
    </template>

    <StudentDashboardNotifications v-else :items="notifications" />

    <StudentCandidateProfileModal
      :candidate="selectedCandidate"
      @close="selectedCandidate = null"
    />
  </div>
</template>
