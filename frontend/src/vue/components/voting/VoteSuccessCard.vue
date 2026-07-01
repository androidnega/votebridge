<script setup>
import { computed } from "vue";

const props = defineProps({
  confirmation: {
    type: Object,
    required: true,
  },
});

const formattedTimestamp = computed(() => {
  if (!props.confirmation.timestamp) return null;
  return new Date(props.confirmation.timestamp).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
});
</script>

<template>
  <article class="overflow-hidden rounded-2xl bg-white shadow-lg ring-1 ring-slate-900/5">
    <div class="bg-success-600 px-6 py-8 text-white sm:px-8">
      <div class="flex items-start gap-4">
        <div
          class="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-white/20 text-2xl"
          aria-hidden="true"
        >
          ✓
        </div>
        <div>
          <h2 class="text-2xl font-bold">Vote Successfully Recorded</h2>
          <p class="mt-1 text-sm text-green-100">
            Thank you for participating. Your selections remain confidential.
          </p>
        </div>
      </div>
    </div>

    <dl class="grid gap-4 px-6 py-6 sm:grid-cols-2 sm:px-8">
      <div class="rounded-lg bg-slate-50 p-4 sm:col-span-2">
        <dt class="text-xs font-medium uppercase tracking-wide text-slate-500">Reference</dt>
        <dd class="mt-1 font-mono text-lg font-semibold text-slate-900">
          {{ confirmation.confirmation_reference || "—" }}
        </dd>
      </div>

      <div class="rounded-lg bg-slate-50 p-4">
        <dt class="text-xs font-medium uppercase tracking-wide text-slate-500">Election</dt>
        <dd class="mt-1 text-base font-semibold text-slate-900">
          {{ confirmation.election_title }}
        </dd>
      </div>

      <div class="rounded-lg bg-slate-50 p-4">
        <dt class="text-xs font-medium uppercase tracking-wide text-slate-500">Submitted</dt>
        <dd class="mt-1 text-base font-semibold text-slate-900">
          {{ formattedTimestamp || "Just now" }}
        </dd>
      </div>
    </dl>

    <p class="border-t border-slate-100 px-6 py-4 text-sm text-slate-600 sm:px-8">
      You cannot vote again in this election. Candidate choices are never shown after submission.
    </p>
  </article>
</template>
