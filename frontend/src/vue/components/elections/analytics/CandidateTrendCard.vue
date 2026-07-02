<script setup>
import CandidateAvatar from "@/components/candidates/CandidateAvatar.vue";

defineProps({
  candidate: { type: Object, required: true },
  compact: { type: Boolean, default: false },
  showPosition: { type: Boolean, default: true },
});
</script>

<template>
  <article
    class="vb-live-trend-card"
    :class="compact ? 'vb-live-trend-card--compact' : ''"
  >
    <CandidateAvatar :candidate="candidate" :size="compact ? 'sm' : 'md'" />
    <div class="min-w-0 flex-1">
      <p class="truncate text-sm font-semibold text-ink-primary">{{ candidate.full_name }}</p>
      <p v-if="showPosition && candidate.position_title" class="truncate text-xs text-ink-secondary">
        {{ candidate.position_title }}
      </p>
      <div class="mt-1.5 flex flex-wrap items-center gap-2">
        <span class="text-sm font-bold tabular-nums text-brand-700">{{ candidate.vote_count ?? 0 }}</span>
        <span class="text-xs text-ink-secondary">votes</span>
        <span
          v-if="candidate.vote_percent !== undefined"
          class="rounded-full bg-brand-50 px-2 py-0.5 text-xs font-semibold text-brand-700"
        >
          {{ candidate.vote_percent }}%
        </span>
        <span
          v-if="candidate.rank"
          class="text-[11px] font-medium uppercase tracking-wide text-ink-secondary"
        >
          #{{ candidate.rank }}
        </span>
      </div>
      <div
        v-if="candidate.vote_percent !== undefined"
        class="mt-2 h-1.5 overflow-hidden rounded-full bg-surface-muted"
      >
        <div
          class="h-full rounded-full bg-brand-600 transition-all duration-500"
          :style="{ width: `${Math.min(100, candidate.vote_percent)}%` }"
        />
      </div>
    </div>
  </article>
</template>
