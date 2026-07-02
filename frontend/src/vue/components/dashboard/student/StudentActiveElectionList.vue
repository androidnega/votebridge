<script setup>
import { useRouter } from "vue-router";
import StudentActiveElectionCard from "./StudentActiveElectionCard.vue";
import { FaIcon, VButton } from "@/components/ui";
import { useVoteEntry } from "@/composables/useVoteEntry";

defineProps({
  elections: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  heading: { type: String, default: "Active elections" },
  headingId: { type: String, default: "active-elections-heading" },
  emptyMessage: {
    type: String,
    default: "There are currently no elections open for voting. You'll be notified when voting begins.",
  },
  showOpenBadge: { type: Boolean, default: true },
});

const router = useRouter();
const { enterVoteFlow, enteringElectionUuid } = useVoteEntry();
</script>

<template>
  <section class="mb-8" :aria-labelledby="headingId">
    <div class="mb-4 flex flex-wrap items-center justify-between gap-3">
      <h2 :id="headingId" class="text-lg font-semibold text-ink-primary sm:text-xl">
        {{ heading }}
      </h2>
      <span
        v-if="showOpenBadge && elections.length"
        class="inline-flex items-center rounded-full bg-success-50 px-3 py-1 text-xs font-semibold text-success-700"
      >
        {{ elections.length }} active
      </span>
    </div>

    <div v-if="loading" class="flex w-full flex-col gap-3">
      <div
        v-for="n in 2"
        :key="n"
        class="h-32 w-full animate-pulse rounded-lg border border-border bg-white"
      />
    </div>

    <div v-else-if="elections.length" class="flex w-full flex-col gap-3">
      <StudentActiveElectionCard
        v-for="election in elections"
        :key="election.uuid"
        :election="election"
        :is-entering="enteringElectionUuid === election.uuid"
        @vote="enterVoteFlow"
      />
    </div>

    <div
      v-else
      class="flex flex-col items-center rounded-xl border border-dashed border-border bg-surface px-5 py-8 text-center"
    >
      <div
        class="mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-surface-muted text-brand-700"
        aria-hidden="true"
      >
        <FaIcon icon="fa-square-poll-vertical" :fixed-width="false" class="text-xl" />
      </div>
      <h3 class="text-base font-semibold text-ink-primary">No Active Elections</h3>
      <p class="mt-2 max-w-md text-sm text-ink-secondary">
        {{ emptyMessage }}
      </p>
      <VButton class="mt-6 min-h-[44px]" variant="secondary" @click="router.push({ name: 'student-my-elections' })">
        View upcoming elections
      </VButton>
    </div>
  </section>
</template>
