<script setup>
import { computed } from "vue";
import ElectionStatusBadge from "./ElectionStatusBadge.vue";

const props = defineProps({
  confirmation: {
    type: Object,
    required: true,
  },
  verification: {
    type: Object,
    default: null,
  },
  verifying: Boolean,
});

const formattedTimestamp = computed(() => {
  if (!props.confirmation.timestamp) return null;
  return new Date(props.confirmation.timestamp).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
});

const verificationStatus = computed(() => {
  if (props.verifying) return "Verifying…";
  if (!props.verification) return null;
  return props.verification.is_valid ? "Verified" : "Verification issue";
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
          <h2 class="text-2xl font-bold">Vote recorded</h2>
          <p class="mt-1 text-sm text-green-100">
            Your ballot has been submitted successfully.
          </p>
        </div>
      </div>
    </div>

    <dl class="grid gap-4 px-6 py-6 sm:grid-cols-2 sm:px-8">
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

      <div class="rounded-lg bg-slate-50 p-4">
        <dt class="text-xs font-medium uppercase tracking-wide text-slate-500">Positions completed</dt>
        <dd class="mt-1 text-base font-semibold text-slate-900">
          {{ confirmation.positions_count ?? confirmation.positions_completed?.length ?? 0 }}
        </dd>
        <ul v-if="confirmation.positions_completed?.length" class="mt-2 space-y-1">
          <li
            v-for="(title, index) in confirmation.positions_completed"
            :key="`${title}-${index}`"
            class="text-sm text-slate-600"
          >
            {{ title }}
          </li>
        </ul>
      </div>

      <div class="rounded-lg bg-slate-50 p-4">
        <dt class="text-xs font-medium uppercase tracking-wide text-slate-500">Verification</dt>
        <dd class="mt-2">
          <ElectionStatusBadge
            v-if="verificationStatus"
            :status="verification?.is_valid ? 'open' : 'paused'"
            :label="verificationStatus"
            size="lg"
          />
          <span v-else class="text-sm text-slate-500">Run verification with your SVT token.</span>
        </dd>
      </div>
    </dl>

    <p class="border-t border-slate-100 px-6 py-4 text-xs text-slate-500 sm:px-8">
      Candidate choices are not shown after submission to protect ballot secrecy.
    </p>
  </article>
</template>
