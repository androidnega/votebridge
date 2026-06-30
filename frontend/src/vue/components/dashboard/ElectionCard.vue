<script setup>
import { computed } from "vue";
import { useRouter } from "vue-router";
import { VButton } from "@/components/ui";
import StatusBadge from "@/components/ui/StatusBadge.vue";

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

const status = computed(
  () => props.election.election_status || props.election.status || "draft"
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
  <article class="vb-surface-panel transition hover:shadow-md">
    <div class="flex items-start justify-between gap-3">
      <div class="min-w-0 flex-1">
        <h3 class="truncate text-base font-semibold text-slate-900">{{ title }}</h3>
        <p v-if="election.start_date" class="mt-1 text-xs text-slate-500">
          {{ formatDate(election.start_date) }}
          <span v-if="election.end_date"> — {{ formatDate(election.end_date) }}</span>
        </p>
      </div>
      <StatusBadge :status="status" size="sm" />
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
          @click="router.push(`/dashboard/elections/${election.uuid || election.election_uuid}`)"
        >
          View details
        </VButton>
      </slot>
    </div>
  </article>
</template>
