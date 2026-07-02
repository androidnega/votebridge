<script setup>
import { computed } from "vue";
import { useRouter } from "vue-router";
import { ResultStatusBadge } from "@/components/results";
import { VButton } from "@/components/ui";

const props = defineProps({
  result: { type: Object, required: true },
  showOfficerActions: { type: Boolean, default: true },
});

const emit = defineEmits(["publish", "archive"]);

const router = useRouter();

const accentClass = computed(() => {
  const map = {
    published: "bg-emerald-500",
    archived: "bg-slate-400",
    certified: "bg-indigo-500",
    pending_certification: "bg-amber-500",
    generated: "bg-amber-500",
    pending_generation: "bg-slate-300",
  };
  return map[props.result.result_status] || "bg-brand-500";
});

const statusMessage = computed(() => {
  const map = {
    published: "Official standings and office holders are available to view and share.",
    archived: "This election is in long-term storage for audit and reference.",
    certified: "Certified and ready for super-admin publication to students.",
    pending_certification: "Voting has ended — results are waiting for governance certification.",
    generated: "Results have been generated and need certification review.",
    pending_generation: "The election is closed and results are still being prepared.",
  };
  return map[props.result.result_status] || "Track progress for this election's results.";
});

const primaryAction = computed(() => {
  const status = props.result.result_status;
  if (["pending_certification", "generated"].includes(status)) {
    return { label: "Open review", route: "result-review" };
  }
  return { label: "View results", route: "result-detail" };
});

const metaItems = computed(() => {
  const items = [];
  if (props.result.turnout_percentage != null) {
    items.push(`${Number(props.result.turnout_percentage).toFixed(1)}% turnout`);
  }
  if (props.result.total_votes_cast != null) {
    items.push(`${props.result.total_votes_cast} votes cast`);
  }
  if (props.result.eligible_voters != null) {
    items.push(`${props.result.eligible_voters} eligible`);
  }
  return items;
});

const dateLabel = computed(() => {
  const value = props.result.published_at || props.result.certified_at || props.result.generated_at;
  if (!value) return null;
  const prefix = props.result.published_at
    ? "Published"
    : props.result.certified_at
      ? "Certified"
      : "Generated";
  return `${prefix} ${new Date(value).toLocaleDateString(undefined, { dateStyle: "medium" })}`;
});

function openPrimary() {
  router.push({
    name: primaryAction.value.route,
    params: { electionUuid: props.result.election_uuid },
  });
}
</script>

<template>
  <article class="relative overflow-hidden rounded-card border border-border bg-white shadow-sm transition hover:shadow-md">
    <div class="absolute inset-y-0 left-0 w-1" :class="accentClass" aria-hidden="true" />

    <div class="flex flex-col gap-4 p-4 pl-5 sm:flex-row sm:items-center sm:justify-between sm:p-5 sm:pl-6">
      <div class="min-w-0 flex-1">
        <div class="flex flex-wrap items-start gap-2">
          <h3 class="text-base font-semibold text-slate-900 sm:text-lg">{{ result.election_title }}</h3>
          <ResultStatusBadge :status="result.result_status" />
        </div>

        <p class="mt-1 text-sm capitalize text-slate-500">
          Election {{ result.election_status || "closed" }}
          <span v-if="dateLabel" class="text-slate-400"> · {{ dateLabel }}</span>
        </p>

        <p v-if="metaItems.length" class="mt-2 text-sm font-medium tabular-nums text-slate-700">
          {{ metaItems.join(" · ") }}
        </p>

        <p class="mt-2 max-w-2xl text-sm leading-relaxed text-slate-600">
          {{ statusMessage }}
        </p>
      </div>

      <div class="flex shrink-0 flex-wrap gap-2 sm:flex-col sm:items-stretch">
        <VButton size="sm" @click="openPrimary">
          {{ primaryAction.label }}
        </VButton>
        <VButton
          v-if="showOfficerActions && result.result_status === 'certified'"
          size="sm"
          variant="secondary"
          @click="emit('publish', result)"
        >
          Publish
        </VButton>
        <VButton
          v-if="showOfficerActions && result.result_status === 'published'"
          size="sm"
          variant="ghost"
          @click="emit('archive', result)"
        >
          Archive
        </VButton>
      </div>
    </div>
  </article>
</template>
