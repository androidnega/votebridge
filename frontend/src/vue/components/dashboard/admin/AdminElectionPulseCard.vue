<script setup>
import { computed } from "vue";
import { StatusBadge } from "@/components/ui";
import AdminMetricProgress from "./AdminMetricProgress.vue";

const props = defineProps({
  election: { type: Object, required: true },
  turnoutMetricLabel: { type: String, default: "Live turnout" },
});

defineEmits(["open"]);

const initials = computed(() => {
  const words = String(props.election.title || "E").split(/\s+/).filter(Boolean);
  return words
    .slice(0, 2)
    .map((word) => word[0])
    .join("")
    .toUpperCase();
});

const readinessPercent = computed(() => {
  const positions = props.election.position_count || 0;
  const approved = props.election.approved_candidate_count || 0;
  if (!positions) return 0;
  return Math.min(100, Math.round((approved / positions) * 100));
});

const approvalPercent = computed(() => {
  const total = props.election.candidate_count || 0;
  const approved = props.election.approved_candidate_count || 0;
  if (!total) return 0;
  return Math.round((approved / total) * 100);
});
</script>

<template>
  <article
    class="flex h-full flex-col rounded-card border border-border bg-white p-5 shadow-[0_1px_3px_0_rgb(15_23_42_/_0.06)] transition duration-200 hover:-translate-y-0.5 hover:shadow-[0_12px_28px_-14px_rgb(15_23_42_/_0.18)]"
  >
    <div class="flex items-start gap-3">
      <span
        class="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-brand-50 text-sm font-bold text-brand-700 ring-2 ring-brand-100"
        aria-hidden="true"
      >
        {{ initials }}
      </span>
      <div class="min-w-0 flex-1">
        <h3 class="truncate text-base font-semibold text-ink-primary">{{ election.title }}</h3>
        <p class="mt-0.5 text-xs text-ink-secondary">{{ election.typeLabel || "Campus election" }}</p>
        <div class="mt-2">
          <StatusBadge :status="election.status" />
        </div>
      </div>
    </div>

    <div class="mt-5 space-y-4">
      <AdminMetricProgress
        :label="turnoutMetricLabel"
        :value="election.turnoutLabel || '—'"
        :percent="election.turnoutPercent || 0"
        tone="brand"
      />
      <AdminMetricProgress
        label="Ballot readiness"
        :value="`${readinessPercent}%`"
        :percent="readinessPercent"
        tone="blue"
      />
      <AdminMetricProgress
        label="Candidates approved"
        :value="`${election.approved_candidate_count || 0} / ${election.candidate_count || 0}`"
        :percent="approvalPercent"
        tone="amber"
      />
      <AdminMetricProgress
        label="Positions configured"
        :value="String(election.position_count || 0)"
        :percent="Math.min(100, (election.position_count || 0) * 12)"
        tone="slate"
      />
    </div>

    <button
      type="button"
      class="mt-5 w-full rounded-input border border-border bg-surface-muted py-2.5 text-sm font-semibold text-brand-700 transition hover:border-brand-200 hover:bg-brand-50"
      @click="$emit('open', election.uuid)"
    >
      Open workspace
    </button>
  </article>
</template>
