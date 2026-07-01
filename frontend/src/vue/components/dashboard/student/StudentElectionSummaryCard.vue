<script setup>
import { computed } from "vue";
import { useRouter } from "vue-router";
import StatusBadge from "@/components/ui/StatusBadge.vue";
import { VButton } from "@/components/ui";

const props = defineProps({
  title: { type: String, required: true },
  status: { type: String, required: true },
  startDate: { type: String, default: null },
  endDate: { type: String, default: null },
  formatDateTime: { type: Function, required: true },
  canVote: { type: Boolean, default: false },
  voteRoute: { type: String, default: null },
});

const router = useRouter();

const dateRange = computed(() => {
  if (!props.startDate && !props.endDate) return null;
  return `${props.formatDateTime(props.startDate)} → ${props.formatDateTime(props.endDate)}`;
});
</script>

<template>
  <article class="rounded-card border border-border bg-surface p-card shadow-card">
    <div class="flex flex-wrap items-start justify-between gap-3">
      <div class="min-w-0 flex-1">
        <h2 class="text-xl font-semibold text-slate-900">{{ title }}</h2>
        <p v-if="dateRange" class="mt-2 text-sm text-slate-600">{{ dateRange }}</p>
      </div>
      <StatusBadge :status="status" />
    </div>

    <dl class="mt-5 grid grid-cols-1 gap-4 sm:grid-cols-2">
      <div class="rounded-input bg-surface-muted px-4 py-3">
        <dt class="text-xs font-semibold uppercase tracking-wide text-slate-500">Opens</dt>
        <dd class="mt-1 text-sm font-medium text-slate-900">{{ formatDateTime(startDate) }}</dd>
      </div>
      <div class="rounded-input bg-surface-muted px-4 py-3">
        <dt class="text-xs font-semibold uppercase tracking-wide text-slate-500">Closes</dt>
        <dd class="mt-1 text-sm font-medium text-slate-900">{{ formatDateTime(endDate) }}</dd>
      </div>
    </dl>

    <VButton
      v-if="canVote && voteRoute"
      class="mt-6 min-h-[48px] w-full"
      @click="router.push(voteRoute)"
    >
      Vote Now
    </VButton>
  </article>
</template>
