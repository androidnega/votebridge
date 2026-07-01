<script setup>
import { useRouter } from "vue-router";
import { VButton } from "@/components/ui";

defineProps({
  elections: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  heading: { type: String, default: "Active elections" },
  headingId: { type: String, default: "active-elections-heading" },
  emptyMessage: {
    type: String,
    default: "No election is currently open. You will receive a notification when voting begins.",
  },
  showOpenBadge: { type: Boolean, default: true },
});

const router = useRouter();
</script>

<template>
  <section class="mb-6" :aria-labelledby="headingId">
    <div class="mb-4 flex flex-wrap items-center justify-between gap-3">
      <h2 :id="headingId" class="text-lg font-semibold text-ink-primary">
        {{ heading }}
      </h2>
      <span
        v-if="showOpenBadge && elections.length"
        class="inline-flex items-center rounded-full bg-success-50 px-3 py-1 text-xs font-semibold text-success-700"
      >
        {{ elections.length }} open
      </span>
    </div>

    <p v-if="loading" class="text-sm text-ink-secondary">Loading elections…</p>

    <div v-else-if="elections.length" class="space-y-4">
      <article
        v-for="election in elections"
        :key="election.uuid"
        class="flex flex-col gap-4 rounded-card border border-border bg-surface p-4 shadow-card sm:flex-row sm:items-center sm:justify-between"
      >
        <div class="flex min-w-0 items-start gap-4">
          <div
            class="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-brand-50 text-sm font-bold text-brand-700"
            aria-hidden="true"
          >
            {{ election.initials }}
          </div>
          <div class="min-w-0">
            <h3 class="text-base font-semibold text-ink-primary">{{ election.title }}</h3>
            <p class="mt-1 text-sm text-ink-secondary">
              <span>{{ election.positionsLabel }}</span>
              <span class="mx-1.5 text-border">·</span>
              <span>{{ election.closesLabel }}</span>
            </p>
            <p v-if="election.hasVoted" class="mt-2 text-xs font-medium text-success-700">
              ✓ Vote recorded
              <span v-if="election.confirmationReference" class="block font-mono text-[11px]">
                {{ election.confirmationReference }}
              </span>
            </p>
            <p v-else-if="election.hasPartialVote" class="mt-2 text-xs font-medium text-warning-700">
              Continue ballot
            </p>
          </div>
        </div>

        <VButton
          v-if="election.canVote"
          class="min-h-[48px] w-full shrink-0 sm:w-auto sm:min-w-[140px]"
          @click="router.push(election.voteRoute)"
        >
          {{ election.hasPartialVote ? "Continue ballot" : "Vote now" }}
        </VButton>
        <VButton
          v-else-if="election.hasVoted"
          variant="secondary"
          class="min-h-[48px] w-full shrink-0 sm:w-auto"
          @click="router.push(`/dashboard/elections/${election.uuid}`)"
        >
          View election
        </VButton>
      </article>
    </div>

    <div
      v-else
      class="rounded-card border border-dashed border-border bg-surface-muted px-4 py-8 text-center text-sm text-ink-secondary"
    >
      {{ emptyMessage }}
    </div>
  </section>
</template>
