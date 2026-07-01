<script setup>
import { computed } from "vue";

const props = defineProps({
  hasVoted: { type: Boolean, default: false },
});

const statusText = computed(() => (props.hasVoted ? "Vote Recorded" : "Not Yet Voted"));

const statusClass = computed(() =>
  props.hasVoted
    ? "border-success-200 bg-success-50 text-success-800"
    : "border-border bg-surface-muted text-slate-800"
);
</script>

<template>
  <section
    class="rounded-card border border-border bg-surface p-card shadow-card"
    aria-labelledby="student-voting-status-heading"
  >
    <h2 id="student-voting-status-heading" class="text-sm font-semibold uppercase tracking-wide text-slate-500">
      Your voting status
    </h2>
    <div
      class="mt-4 flex min-h-[56px] items-center rounded-input border px-4 py-3"
      :class="statusClass"
    >
      <span class="text-lg font-semibold">{{ statusText }}</span>
    </div>
    <p class="mt-3 text-sm text-slate-600">
      {{
        hasVoted
          ? "Thank you for participating. Your ballot is sealed and cannot be changed."
          : "You have not submitted a ballot for the current election."
      }}
    </p>
  </section>
</template>
