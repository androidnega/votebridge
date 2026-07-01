<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { dashboardApi } from "@/api";
import StatusBadge from "@/components/ui/StatusBadge.vue";
import { LoadingSkeleton, VAlert, VButton } from "@/components/ui";
import { extractApiError } from "@/api/helpers";
import { useElectionRealtime } from "@/composables/useElectionRealtime";
import { useVotingStore } from "@/stores/voting";

const route = useRoute();
const router = useRouter();
const votingStore = useVotingStore();

const electionUuid = computed(() => route.params.uuid);
const detail = ref(null);
const loading = ref(true);
const error = ref(null);

const { electionStatus } = useElectionRealtime(electionUuid);

function formatDateTime(value) {
  if (!value) return "Date to be announced";
  return new Date(value).toLocaleString(undefined, {
    day: "numeric",
    month: "long",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

const liveStatus = computed(
  () => electionStatus.value || detail.value?.election_status || "draft"
);

const statusLabel = computed(
  () => detail.value?.election_status_display || liveStatus.value.replace(/_/g, " ")
);

const votingPeriod = computed(() => {
  if (!detail.value?.start_date && !detail.value?.end_date) return null;
  return `${formatDateTime(detail.value.start_date)} — ${formatDateTime(detail.value.end_date)}`;
});

const positions = computed(() => detail.value?.positions || []);

const allPositionsVoted = computed(
  () => positions.value.length > 0 && positions.value.every((position) => position.has_voted)
);

const continueLabel = computed(() => {
  if (allPositionsVoted.value) return "View confirmation";
  if (detail.value?.next_position_title) {
    return `Continue to ${detail.value.next_position_title} →`;
  }
  return "Start voting →";
});

const canContinue = computed(() => {
  if (!detail.value) return false;
  if (liveStatus.value === "paused") return false;
  if (allPositionsVoted.value) return true;
  return detail.value.can_vote && liveStatus.value === "open";
});

async function loadDetail() {
  loading.value = true;
  error.value = null;
  try {
    detail.value = await dashboardApi.getStudentElectionDetail(electionUuid.value);
  } catch (err) {
    error.value = extractApiError(err);
  } finally {
    loading.value = false;
  }
}

function goToPosition(position) {
  if (liveStatus.value !== "open" || position.has_voted) return;
  router.push({
    path: `/dashboard/elections/${electionUuid.value}/vote`,
    query: { position: position.uuid },
  });
}

function handleContinue() {
  if (allPositionsVoted.value) {
    router.push(`/dashboard/elections/${electionUuid.value}/confirmation`);
    return;
  }

  const query = detail.value?.next_position_uuid
    ? { position: detail.value.next_position_uuid }
    : undefined;
  router.push({
    path: `/dashboard/elections/${electionUuid.value}/vote`,
    query,
  });
}

function candidateLabel(count) {
  const total = count ?? 0;
  if (total === 0) return "No approved candidates yet";
  return `${total} candidate${total === 1 ? "" : "s"} contesting`;
}

watch(electionUuid, () => {
  loadDetail().catch(() => {});
});

watch(
  () => votingStore.ballotSubmitted,
  (submitted) => {
    if (submitted) loadDetail().catch(() => {});
  }
);

watch(liveStatus, (status, previous) => {
  if (status && status !== previous) {
    loadDetail().catch(() => {});
  }
});

onMounted(() => {
  loadDetail().catch(() => {});
});
</script>

<template>
  <div>
    <LoadingSkeleton v-if="loading && !detail" variant="card" :rows="4" />

    <template v-else-if="detail">
      <header class="mb-6">
        <div class="flex flex-wrap items-center gap-3">
          <h1 class="text-2xl font-bold tracking-tight text-ink-primary sm:text-3xl">
            {{ detail.election_title }}
          </h1>
          <StatusBadge :status="liveStatus" :label="statusLabel" size="sm" />
        </div>
        <p v-if="votingPeriod" class="mt-2 text-sm text-ink-secondary sm:text-base">
          {{ votingPeriod }}
        </p>
        <p v-if="detail.election_type_display" class="mt-1 text-sm text-ink-secondary">
          {{ detail.election_type_display }} election
        </p>
        <p v-if="detail.description" class="mt-2 max-w-3xl text-sm text-ink-secondary">
          {{ detail.description }}
        </p>
      </header>

      <VAlert v-if="error" class="mb-4" variant="error">{{ error }}</VAlert>

      <VAlert
        v-if="liveStatus === 'paused'"
        class="mb-4"
        variant="warning"
        title="Voting paused"
      >
        This election is temporarily paused. Check back when voting resumes.
      </VAlert>

      <section
        class="rounded-card border border-border bg-surface shadow-card"
        aria-labelledby="position-list-heading"
      >
        <div class="border-b border-border px-5 py-4 sm:px-6">
          <h2 id="position-list-heading" class="text-base font-semibold text-ink-primary">
            Select a position to vote
          </h2>
          <p class="mt-1 text-sm text-ink-secondary">
            {{ detail.positions_count }} position{{ detail.positions_count === 1 ? "" : "s" }} on
            your ballot
          </p>
        </div>

        <ul v-if="positions.length" role="list" class="divide-y divide-border">
          <li
            v-for="position in positions"
            :key="position.uuid"
          >
            <button
              type="button"
              class="flex w-full flex-col gap-3 px-5 py-4 text-left transition hover:bg-surface-muted sm:flex-row sm:items-center sm:justify-between sm:px-6"
              :class="
                liveStatus === 'open' && !position.has_voted
                  ? 'cursor-pointer'
                  : 'cursor-default'
              "
              :disabled="liveStatus !== 'open' || position.has_voted"
              @click="goToPosition(position)"
            >
              <div class="min-w-0">
                <p class="text-base font-semibold text-ink-primary">{{ position.title }}</p>
                <p class="mt-1 text-sm text-ink-secondary">
                  {{ candidateLabel(position.candidate_count) }}
                </p>
              </div>
              <span
                class="inline-flex w-fit shrink-0 items-center rounded-full px-3 py-1 text-xs font-semibold"
                :class="
                  position.has_voted
                    ? 'bg-success-50 text-success-700'
                    : 'bg-warning-50 text-warning-700'
                "
              >
                {{ position.has_voted ? "Voted" : "Not voted" }}
              </span>
            </button>
          </li>
        </ul>

        <p v-else class="px-5 py-8 text-center text-sm text-ink-secondary sm:px-6">
          No votable positions are on your ballot yet. Approved candidates may still be pending.
        </p>
      </section>

      <div class="mt-6 flex flex-wrap gap-3">
        <VButton v-if="canContinue" class="min-h-[48px]" @click="handleContinue">
          {{ continueLabel }}
        </VButton>
        <VButton
          variant="secondary"
          class="min-h-[48px]"
          @click="router.push('/dashboard/my-elections')"
        >
          Back to my elections
        </VButton>
      </div>
    </template>

    <VAlert v-else variant="error" title="Election unavailable">
      {{ error || "This election could not be loaded." }}
    </VAlert>
  </div>
</template>
