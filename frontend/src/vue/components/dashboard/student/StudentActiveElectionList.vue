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
const { enterVoteFlow, entering } = useVoteEntry();
</script>

<template>
  <section class="mb-8" :aria-labelledby="headingId">
    <div class="mb-6 flex flex-wrap items-center justify-between gap-3">
      <h2 :id="headingId" class="text-xl font-semibold text-ink-primary sm:text-2xl">
        {{ heading }}
      </h2>
      <span
        v-if="showOpenBadge && elections.length"
        class="inline-flex items-center rounded-full bg-success-50 px-3 py-1 text-xs font-semibold text-success-700"
      >
        {{ elections.length }} active
      </span>
    </div>

    <div v-if="loading" class="grid grid-cols-1 gap-6 md:grid-cols-2">
      <div
        v-for="n in 2"
        :key="n"
        class="h-80 animate-pulse rounded-2xl border border-border bg-surface"
      />
    </div>

    <div v-else-if="elections.length" class="grid grid-cols-1 gap-6 md:grid-cols-2">
      <StudentActiveElectionCard
        v-for="election in elections"
        :key="election.uuid"
        :election="election"
        :action-loading="entering"
        @vote="enterVoteFlow"
      />
    </div>

    <div
      v-else
      class="flex flex-col items-center rounded-2xl border border-dashed border-border bg-surface px-6 py-12 text-center"
    >
      <div
        class="mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-surface-muted text-2xl text-brand-700"
        aria-hidden="true"
      >
        <FaIcon icon="fa-box-ballot" :fixed-width="false" />
      </div>
      <h3 class="text-lg font-semibold text-ink-primary">No Active Elections</h3>
      <p class="mt-2 max-w-md text-sm text-ink-secondary">
        {{ emptyMessage }}
      </p>
      <VButton class="mt-6 min-h-[44px]" variant="secondary" @click="router.push({ name: 'student-my-elections' })">
        View upcoming elections
      </VButton>
    </div>
  </section>
</template>
