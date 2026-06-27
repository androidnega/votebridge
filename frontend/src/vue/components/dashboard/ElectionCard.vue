<script setup>
import { computed } from "vue";
import { useRouter } from "vue-router";
import { VButton } from "@/components/ui";

const props = defineProps({
  election: {
    type: Object,
    required: true,
  },
  showConfirmation: {
    type: Boolean,
    default: false,
  },
});

const router = useRouter();

const statusClasses = computed(() => {
  const map = {
    draft: "bg-slate-100 text-slate-700",
    scheduled: "bg-blue-50 text-blue-700",
    open: "bg-green-50 text-green-700",
    paused: "bg-amber-50 text-amber-700",
    closed: "bg-slate-200 text-slate-700",
    archived: "bg-slate-100 text-slate-500",
  };
  const status = props.election.election_status || props.election.status;
  return map[status] || map.draft;
});

const statusLabel = computed(
  () => props.election.election_status || props.election.status || "unknown"
);

const title = computed(
  () => props.election.election_title || props.election.title || "Untitled election"
);

const confirmationLabel = computed(() => {
  const map = {
    recorded: "Vote recorded",
    in_progress: "Ballot in progress",
    token_issued: "Token issued",
    not_started: "Not started",
  };
  return map[props.election.confirmation_status] || null;
});

function formatDate(value) {
  if (!value) return null;
  return new Date(value).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}
</script>

<template>
  <article class="flex flex-col rounded-xl bg-white p-5 shadow-sm ring-1 ring-slate-900/5 transition hover:shadow-md">
    <div class="flex items-start justify-between gap-3">
      <div class="min-w-0 flex-1">
        <h3 class="truncate text-base font-semibold text-slate-900">{{ title }}</h3>
        <p v-if="election.start_date" class="mt-1 text-xs text-slate-500">
          {{ formatDate(election.start_date) }}
          <span v-if="election.end_date"> — {{ formatDate(election.end_date) }}</span>
        </p>
      </div>
      <span
        class="inline-flex shrink-0 rounded-full px-2.5 py-0.5 text-xs font-medium capitalize"
        :class="statusClasses"
      >
        {{ statusLabel }}
      </span>
    </div>

    <p
      v-if="showConfirmation && confirmationLabel"
      class="mt-3 text-sm text-slate-600"
    >
      Status: <span class="font-medium text-slate-900">{{ confirmationLabel }}</span>
    </p>

    <div v-if="$slots.actions || election.uuid || election.election_uuid" class="mt-4 flex flex-wrap gap-2">
      <slot name="actions">
        <VButton
          size="sm"
          variant="secondary"
          @click="router.push(`/elections/${election.uuid || election.election_uuid}`)"
        >
          View details
        </VButton>
      </slot>
    </div>
  </article>
</template>
