<script setup>
import { computed } from "vue";
import ConnectionStatusIndicator from "./ConnectionStatusIndicator.vue";

const props = defineProps({
  percentage: {
    type: Number,
    default: 0,
  },
  votesCast: {
    type: Number,
    default: 0,
  },
  registeredVoters: {
    type: Number,
    default: 0,
  },
  loading: Boolean,
  live: Boolean,
  status: {
    type: String,
    default: "disconnected",
  },
});

const clampedPercentage = computed(() =>
  Math.min(100, Math.max(0, Number(props.percentage) || 0))
);

const participationLabel = computed(() => {
  if (!props.registeredVoters) return `${props.votesCast} votes cast`;
  return `${props.votesCast} of ${props.registeredVoters} voters`;
});
</script>

<template>
  <section class="rounded-xl bg-white p-5 shadow-sm ring-1 ring-slate-900/5">
    <div class="flex items-start justify-between gap-3">
      <div>
        <p class="text-xs font-medium uppercase tracking-wide text-slate-500">Live turnout</p>
        <p class="mt-1 text-3xl font-bold tabular-nums text-slate-900">
          <span v-if="loading" class="inline-block h-8 w-16 animate-pulse rounded bg-slate-200" />
          <span v-else>{{ clampedPercentage }}%</span>
        </p>
        <p class="mt-1 text-sm text-slate-500">{{ participationLabel }}</p>
      </div>
      <ConnectionStatusIndicator v-if="live" :status="status" />
    </div>

    <div class="mt-4">
      <div class="h-2.5 overflow-hidden rounded-full bg-slate-100">
        <div
          class="h-full rounded-full bg-brand-600 transition-all duration-500 ease-out"
          :class="{ 'animate-pulse': live && status === 'connected' }"
          :style="{ width: `${clampedPercentage}%` }"
        />
      </div>
    </div>

    <p class="mt-3 text-xs text-slate-400">
      Aggregate participation only — candidate totals are hidden while elections are open.
    </p>
  </section>
</template>
