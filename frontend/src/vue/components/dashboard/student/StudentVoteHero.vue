<script setup>
import { useRouter } from "vue-router";
import StatusBadge from "@/components/ui/StatusBadge.vue";
import { VButton } from "@/components/ui";

defineProps({
  greeting: { type: String, required: true },
  studentName: { type: String, required: true },
  electionTitle: { type: String, default: "" },
  electionStatus: { type: String, default: "draft" },
  countdownLabel: { type: String, default: "Closes in" },
  countdownText: { type: String, default: "—" },
  canVote: { type: Boolean, default: false },
  voteRoute: { type: String, default: null },
  hasActiveElection: { type: Boolean, default: false },
});

const router = useRouter();
</script>

<template>
  <section
    class="rounded-card bg-brand-700 px-5 py-8 text-white shadow-card sm:px-8 sm:py-10"
    aria-labelledby="student-vote-hero-heading"
  >
    <p class="text-sm font-medium text-brand-100">{{ greeting }}</p>
    <h1 id="student-vote-hero-heading" class="mt-1 text-3xl font-bold tracking-tight sm:text-4xl">
      {{ studentName }}
    </h1>

    <template v-if="hasActiveElection">
      <div class="mt-6 flex flex-wrap items-center gap-3">
        <p class="text-lg font-semibold text-white">{{ electionTitle }}</p>
        <StatusBadge :status="electionStatus" size="sm" />
      </div>
      <p class="mt-3 text-sm text-brand-100">
        {{ countdownLabel }}:
        <span class="font-semibold text-white">{{ countdownText }}</span>
      </p>
      <VButton
        v-if="canVote && voteRoute"
        class="mt-8 min-h-[52px] w-full text-base font-semibold sm:w-auto sm:min-w-[220px]"
        size="lg"
        variant="secondary"
        @click="router.push(voteRoute)"
      >
        Vote Now
      </VButton>
      <p v-else-if="electionStatus === 'paused'" class="mt-6 text-sm text-brand-100">
        Voting is temporarily paused. Check back soon.
      </p>
      <p v-else-if="!canVote" class="mt-6 text-sm text-brand-100">
        Your ballot has been recorded for this election.
      </p>
    </template>

    <template v-else>
      <p class="mt-6 max-w-md text-base leading-relaxed text-brand-50">
        No election is currently open.
      </p>
      <p class="mt-2 max-w-md text-sm text-brand-100">
        You will receive a notification when voting begins.
      </p>
    </template>
  </section>
</template>
