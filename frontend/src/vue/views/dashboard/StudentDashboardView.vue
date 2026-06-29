<script setup>
import { computed, onMounted, ref } from "vue";
import {
  ConnectionStatusIndicator,
  ElectionCard,
  EmptyState,
  LoadingSkeleton,
  StatCard,
} from "@/components/dashboard";
import { VAlert, VButton, VInput } from "@/components/ui";
import { emptyStates } from "@/config/emptyStates";
import { useDashboardRealtime } from "@/composables/useDashboardRealtime";
import { useAuthStore } from "@/stores/auth";
import { useDashboardStore } from "@/stores/dashboard";

const authStore = useAuthStore();
const dashboardStore = useDashboardStore();
const realtime = useDashboardRealtime("student");

const verifyToken = ref("");

const greeting = computed(() => {
  const hour = new Date().getHours();
  if (hour < 12) return "Good morning";
  if (hour < 17) return "Good afternoon";
  return "Good evening";
});

const confirmationStats = computed(
  () => dashboardStore.studentOverview?.vote_confirmation_status || {}
);

onMounted(() => {
  dashboardStore.fetchStudentDashboard().catch(() => {});
});
</script>

<template>
  <div class="space-y-8">
    <section class="rounded-2xl bg-brand-700 px-6 py-8 text-white shadow-sm sm:px-8">
      <div class="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p class="text-sm font-medium text-brand-100">{{ greeting }}</p>
          <h2 class="mt-1 text-2xl font-bold sm:text-3xl">
            {{ authStore.fullName || authStore.user?.email || "Voter" }}
          </h2>
          <p class="mt-2 max-w-xl text-sm text-brand-100">
            Track active elections, review your voting history, and verify ballots from one place.
          </p>
        </div>
        <ConnectionStatusIndicator
          class="shrink-0"
          :status="realtime.status.value"
          :label="realtime.label.value"
        />
      </div>
    </section>

    <VAlert v-if="dashboardStore.error" variant="error">
      {{ dashboardStore.error }}
    </VAlert>

    <LoadingSkeleton v-if="dashboardStore.loading && !dashboardStore.studentOverview" variant="stats" :rows="3" />

    <section v-else class="grid grid-cols-1 gap-4 sm:grid-cols-3">
      <StatCard
        label="Active elections"
        :value="dashboardStore.studentOverview?.active_elections_count ?? 0"
        hint="Open or paused elections you can vote in"
        accent="green"
      />
      <StatCard
        label="Votes recorded"
        :value="confirmationStats.recorded ?? 0"
        hint="Completed ballots this cycle"
        accent="brand"
      />
      <StatCard
        label="Pending"
        :value="confirmationStats.pending ?? 0"
        hint="Elections awaiting your vote"
        accent="amber"
      />
    </section>

    <section>
      <div class="mb-4 flex items-center justify-between">
        <h3 class="text-lg font-semibold text-slate-900">Active elections</h3>
      </div>
      <LoadingSkeleton v-if="dashboardStore.loading" variant="card" />
      <EmptyState
        v-else-if="dashboardStore.studentActiveElections.length === 0"
        v-bind="emptyStates.studentActive"
      />
      <div v-else class="grid grid-cols-1 gap-4 md:grid-cols-2">
        <ElectionCard
          v-for="election in dashboardStore.studentActiveElections"
          :key="election.election_uuid"
          :election="election"
          show-confirmation
        />
      </div>
    </section>

    <section>
      <h3 class="mb-4 text-lg font-semibold text-slate-900">Upcoming elections</h3>
      <LoadingSkeleton v-if="dashboardStore.loading" variant="card" />
      <EmptyState
        v-else-if="dashboardStore.scheduledElections.length === 0"
        v-bind="emptyStates.studentUpcoming"
      />
      <div v-else class="grid grid-cols-1 gap-4 md:grid-cols-2">
        <ElectionCard
          v-for="election in dashboardStore.scheduledElections"
          :key="election.uuid"
          :election="election"
        />
      </div>
    </section>

    <section>
      <h3 class="mb-4 text-lg font-semibold text-slate-900">Voting history</h3>
      <EmptyState
        v-if="!dashboardStore.loading && dashboardStore.studentVotingHistory.length === 0"
        v-bind="emptyStates.voteHistory"
      />
      <div v-else class="grid grid-cols-1 gap-4 md:grid-cols-2">
        <ElectionCard
          v-for="election in dashboardStore.studentVotingHistory"
          :key="`history-${election.election_uuid}`"
          :election="election"
          show-confirmation
        />
      </div>
    </section>

    <section class="rounded-xl bg-white p-6 shadow-sm ring-1 ring-slate-900/5">
      <h3 class="text-lg font-semibold text-slate-900">Verification center</h3>
      <p class="mt-1 text-sm text-slate-500">
        Enter your Secure Voting Token to confirm your ballot was recorded. Candidate choices are never shown.
      </p>

      <form
        class="mt-4 flex flex-col gap-3 sm:flex-row sm:items-end"
        @submit.prevent="dashboardStore.verifyBallotToken(verifyToken)"
      >
        <div class="flex-1">
          <VInput
            v-model="verifyToken"
            label="SVT token"
            placeholder="Paste your voting token"
            autocomplete="off"
          />
        </div>
        <VButton type="submit" :loading="dashboardStore.verifying">Verify ballot</VButton>
      </form>

      <VAlert
        v-if="dashboardStore.verificationResult"
        class="mt-4"
        variant="success"
        :title="dashboardStore.verificationResult.is_valid ? 'Ballot verified' : 'Verification issue'"
      >
        <p class="text-sm">
          {{ dashboardStore.verificationResult.election_title }} —
          {{ dashboardStore.verificationResult.positions_count }} position(s) completed.
        </p>
      </VAlert>
    </section>
  </div>
</template>
