<script setup>
import { computed, ref } from "vue";
import AdminCandidateSpotlightCard from "./AdminCandidateSpotlightCard.vue";
import { useElectionLiveTrend } from "@/composables/useElectionLiveTrend";
import { EmptyState, LoadingSkeleton, StatusBadge, VButton } from "@/components/ui";

const props = defineProps({
  election: { type: Object, default: null },
  candidates: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
});

defineEmits(["open-workspace"]);

const scroller = ref(null);
const isElectionLive = computed(() => ["open", "paused"].includes(props.election?.status));

const {
  positions: livePositions,
  loading: trendLoading,
  hasVotes,
} = useElectionLiveTrend(() => (isElectionLive.value ? props.election?.uuid : null));

const liveCandidateMap = computed(() => {
  const map = new Map();
  for (const position of livePositions.value || []) {
    for (const candidate of position.candidates || []) {
      map.set(candidate.candidate_uuid, {
        ...candidate,
        position_title: position.position_title,
      });
    }
  }
  return map;
});

const displayCandidates = computed(() => {
  const merged = props.candidates.map((candidate) => {
    const live = liveCandidateMap.value.get(candidate.uuid);
    return {
      ...candidate,
      position_title: candidate.position_title || live?.position_title,
      vote_count: live?.vote_count ?? 0,
      vote_percent: live?.vote_percent ?? 0,
      rank: live?.rank ?? null,
      image_path: live?.image_path || candidate.image_path,
    };
  });

  if (isElectionLive.value && hasVotes.value) {
    return [...merged].sort((left, right) => (right.vote_count || 0) - (left.vote_count || 0));
  }

  return merged;
});

const showLoading = computed(() => props.loading || (isElectionLive.value && trendLoading.value && !displayCandidates.value.length));

function scrollBy(direction) {
  if (!scroller.value) return;
  const amount = direction === "left" ? -220 : 220;
  scroller.value.scrollBy({ left: amount, behavior: "smooth" });
}
</script>

<template>
  <section aria-labelledby="election-candidate-spotlight-heading">
    <div class="mb-4 flex flex-wrap items-end justify-between gap-3">
      <div class="min-w-0">
        <h2 id="election-candidate-spotlight-heading" class="text-lg font-semibold text-ink-primary">
          Election spotlight
        </h2>
        <p v-if="election" class="mt-1 text-sm text-ink-secondary">
          <span class="font-medium text-ink-primary">{{ election.title }}</span>
          — scroll to browse candidates
          <span v-if="isElectionLive">; trends update live as ballots are cast.</span>
          <span v-else>; live trends appear when voting opens.</span>
        </p>
        <p v-else class="mt-1 text-sm text-ink-secondary">
          Candidate cards will appear here when an election is scheduled or open.
        </p>
      </div>

      <div class="flex shrink-0 items-center gap-2 sm:gap-3">
        <StatusBadge v-if="election" :status="election.status" size="sm" />
        <div v-if="displayCandidates.length > 2" class="hidden gap-2 sm:flex">
          <button
            type="button"
            class="rounded-input border border-border bg-white px-3 py-1.5 text-sm font-medium text-slate-600 hover:bg-surface-muted"
            aria-label="Scroll left"
            @click="scrollBy('left')"
          >
            ←
          </button>
          <button
            type="button"
            class="rounded-input border border-border bg-white px-3 py-1.5 text-sm font-medium text-slate-600 hover:bg-surface-muted"
            aria-label="Scroll right"
            @click="scrollBy('right')"
          >
            →
          </button>
        </div>
        <VButton
          v-if="election"
          variant="secondary"
          size="sm"
          @click="$emit('open-workspace', election.uuid)"
        >
          Manage
        </VButton>
      </div>
    </div>

    <LoadingSkeleton v-if="showLoading" variant="stats" :rows="4" />

    <div
      v-else-if="election && displayCandidates.length"
      ref="scroller"
      class="vb-spotlight-scroll flex gap-3 overflow-x-auto pb-2 pt-1 sm:gap-4"
      tabindex="0"
      role="list"
      aria-label="Election candidates"
    >
      <AdminCandidateSpotlightCard
        v-for="candidate in displayCandidates"
        :key="candidate.uuid"
        :candidate="candidate"
        :is-live="isElectionLive"
        role="listitem"
      />
    </div>

    <EmptyState
      v-else
      icon="profile"
      :title="election ? 'No approved candidates yet' : 'No upcoming election'"
      :description="
        election
          ? 'Approve nominated candidates to display them here.'
          : 'Schedule or open an election to showcase candidates here.'
      "
    />
  </section>
</template>

<style scoped>
.vb-spotlight-scroll {
  scroll-snap-type: x mandatory;
  scroll-padding-inline: 4px;
  -webkit-overflow-scrolling: touch;
}

.vb-spotlight-scroll::-webkit-scrollbar {
  height: 6px;
}

.vb-spotlight-scroll::-webkit-scrollbar-thumb {
  border-radius: 999px;
  background: rgb(203 213 225);
}
</style>
