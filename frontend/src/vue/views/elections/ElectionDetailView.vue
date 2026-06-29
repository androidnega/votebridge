<script setup>
import { computed, onMounted, onUnmounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { LoadingSkeleton } from "@/components/dashboard";
import { ElectionReadinessPanel } from "@/components/elections";
import {
  CandidateCard,
  CountdownTimer,
  ElectionStatusBadge,
} from "@/components/voting";
import { VAlert, VButton } from "@/components/ui";
import { useElectionRealtime } from "@/composables/useElectionRealtime";
import { useAuthStore } from "@/stores/auth";
import { useElectionStore } from "@/stores/election";
import { useVotingStore } from "@/stores/voting";

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const electionStore = useElectionStore();
const votingStore = useVotingStore();

const electionUuid = computed(() => route.params.uuid);
const election = computed(() => electionStore.currentElection || {});
const liveStatus = computed(
  () => votingStore.electionStatus || election.value.status
);

const canVote = computed(() => {
  if (!authStore.isStudent) return false;
  return ["open", "paused"].includes(liveStatus.value);
});

const alreadyVoted = computed(
  () => votingStore.ballotSubmitted || votingStore.confirmationStatus === "recorded"
);

const previewCandidates = computed(() => {
  if (votingStore.previewPositions.length && authStore.isElectionOfficer) {
    return votingStore.previewCandidates.slice(0, 6);
  }
  return votingStore.previewCandidates.slice(0, 6);
});

const positionsSummary = computed(() => {
  if (votingStore.previewPositions.length) {
    return votingStore.previewPositions;
  }
  const count = election.value.position_count || 0;
  if (!count) return [];
  return Array.from({ length: Math.min(count, 6) }, (_, i) => ({
    uuid: `placeholder-${i}`,
    title: `Position ${i + 1}`,
  }));
});

const groupedCandidates = computed(() => {
  if (!authStore.isElectionOfficer) {
    return votingStore.previewPositions.map((position) => ({
      position,
      candidates: (position.candidates || []).slice(0, 3),
    }));
  }
  const byPosition = {};
  for (const candidate of votingStore.previewCandidates) {
    const key = candidate.position_uuid || "unknown";
    if (!byPosition[key]) {
      byPosition[key] = {
        position: {
          uuid: key,
          title: candidate.position_title || "Position",
        },
        candidates: [],
      };
    }
    if (byPosition[key].candidates.length < 3) {
      byPosition[key].candidates.push(candidate);
    }
  }
  return Object.values(byPosition);
});

const showReadiness = computed(() => {
  if (!authStore.isElectionOfficer) return false;
  return ["draft", "scheduled"].includes(liveStatus.value);
});

const canOpenElection = computed(
  () => showReadiness.value && electionStore.readinessReport?.is_ready
);

async function loadReadiness() {
  if (!showReadiness.value) return;
  await electionStore.fetchReadiness(electionUuid.value).catch(() => {});
}

async function handleOpenElection() {
  await electionStore.openElection(electionUuid.value);
}

useElectionRealtime(electionUuid);

onMounted(async () => {
  await electionStore.fetchElection(electionUuid.value).catch(() => {});
  await loadReadiness();
  await votingStore
    .fetchPreviewData(electionUuid.value, { isAdmin: authStore.isElectionOfficer })
    .catch(() => {});
});

watch(showReadiness, (visible) => {
  if (visible) loadReadiness();
});

onUnmounted(() => {
  electionStore.clearCurrent();
});
</script>

<template>
  <div class="space-y-8">
    <section
      class="overflow-hidden rounded-2xl bg-brand-800 px-6 py-8 text-white shadow-sm sm:px-8"
    >
      <div class="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
        <div class="min-w-0 flex-1">
          <div class="flex flex-wrap items-center gap-3">
            <ElectionStatusBadge
              :status="liveStatus"
              :label="election.status_display"
              size="lg"
            />
          </div>
          <h2 class="mt-4 text-2xl font-bold sm:text-3xl">
            {{ election.title || "Election" }}
          </h2>
          <p v-if="election.description" class="mt-3 max-w-2xl text-sm text-brand-100">
            {{ election.description }}
          </p>
          <dl class="mt-4 flex flex-wrap gap-4 text-sm text-brand-100">
            <div v-if="election.election_type_display">
              <dt class="sr-only">Type</dt>
              <dd>{{ election.election_type_display }}</dd>
            </div>
            <div v-if="election.start_date">
              <dt class="font-medium">Starts</dt>
              <dd>{{ new Date(election.start_date).toLocaleString() }}</dd>
            </div>
            <div v-if="election.end_date">
              <dt class="font-medium">Ends</dt>
              <dd>{{ new Date(election.end_date).toLocaleString() }}</dd>
            </div>
          </dl>
        </div>
        <CountdownTimer
          :start-date="election.start_date"
          :end-date="election.end_date"
          :status="liveStatus"
        />
      </div>

      <div v-if="canVote" class="mt-6 flex flex-wrap gap-3">
        <VButton
          v-if="!alreadyVoted"
          size="lg"
          @click="router.push(`/elections/${electionUuid}/vote`)"
        >
          Cast your vote
        </VButton>
        <VButton
          v-else
          size="lg"
          variant="secondary"
          @click="router.push(`/elections/${electionUuid}/confirmation`)"
        >
          View confirmation
        </VButton>
      </div>
    </section>

    <VAlert v-if="electionStore.error" variant="error">{{ electionStore.error }}</VAlert>

    <section v-if="showReadiness" class="space-y-4">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <h3 class="text-lg font-semibold text-slate-900">Pre-open readiness</h3>
        <div class="flex flex-wrap gap-2">
          <VButton
            variant="secondary"
            size="sm"
            :loading="electionStore.readinessLoading"
            @click="loadReadiness"
          >
            Refresh checklist
          </VButton>
          <VButton
            v-if="election.status === 'scheduled'"
            size="sm"
            :loading="electionStore.actionLoading"
            :disabled="!canOpenElection"
            @click="handleOpenElection"
          >
            Open election
          </VButton>
        </div>
      </div>
      <ElectionReadinessPanel
        :report="electionStore.readinessReport"
        :loading="electionStore.readinessLoading"
      />
    </section>

    <LoadingSkeleton v-if="electionStore.loading && !election.title" variant="card" />

    <section v-else class="grid grid-cols-1 gap-6 lg:grid-cols-3">
      <div class="lg:col-span-1">
        <div class="rounded-xl bg-white p-6 shadow-sm ring-1 ring-slate-900/5">
          <h3 class="text-lg font-semibold text-slate-900">Positions</h3>
          <p class="mt-1 text-sm text-slate-500">
            {{ election.position_count ?? positionsSummary.length }} position(s) on this ballot
          </p>
          <ul class="mt-4 space-y-2">
            <li
              v-for="position in positionsSummary"
              :key="position.uuid"
              class="rounded-lg bg-slate-50 px-3 py-2 text-sm text-slate-700"
            >
              {{ position.title }}
              <span
                v-if="position.choice_type"
                class="ml-2 text-xs capitalize text-slate-500"
              >
                ({{ position.choice_type }})
              </span>
            </li>
          </ul>
          <dl class="mt-6 grid grid-cols-2 gap-3 text-sm">
            <div class="rounded-lg bg-brand-50 p-3">
              <dt class="text-brand-700">Candidates</dt>
              <dd class="text-lg font-semibold text-brand-900">
                {{ election.approved_candidate_count ?? election.candidate_count ?? "—" }}
              </dd>
            </div>
            <div class="rounded-lg bg-slate-50 p-3">
              <dt class="text-slate-500">Status</dt>
              <dd class="text-lg font-semibold capitalize text-slate-900">{{ liveStatus }}</dd>
            </div>
          </dl>
        </div>
      </div>

      <div class="lg:col-span-2">
        <h3 class="mb-4 text-lg font-semibold text-slate-900">Candidate preview</h3>
        <LoadingSkeleton v-if="votingStore.loading" variant="card" />
        <VAlert
          v-else-if="!groupedCandidates.length"
          variant="info"
          title="Preview unavailable"
        >
          Candidate details will appear when the ballot is published and voting opens.
        </VAlert>
        <div v-else class="space-y-6">
          <div v-for="group in groupedCandidates" :key="group.position.uuid">
            <h4 class="mb-3 text-sm font-semibold text-slate-700">{{ group.position.title }}</h4>
            <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
              <CandidateCard
                v-for="candidate in group.candidates"
                :key="candidate.uuid"
                :candidate="candidate"
                :selected="false"
                disabled
                :tab-index="-1"
              />
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>
