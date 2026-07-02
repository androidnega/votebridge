<script setup>
import { computed } from "vue";
import { getCandidatePhotoUrl } from "@/utils/candidateDisplay";

const props = defineProps({
  candidate: { type: Object, required: true },
  isLive: { type: Boolean, default: false },
});

const photoUrl = computed(() =>
  getCandidatePhotoUrl({
    ...props.candidate,
    image_url: props.candidate.image_url || props.candidate.image_path,
  })
);

const trendPercent = computed(() => {
  const value = Number(props.candidate.vote_percent);
  return Number.isFinite(value) ? Math.min(100, Math.max(0, value)) : 0;
});

const trendLabel = computed(() => {
  if (!props.isLive) return "Awaiting votes";
  if ((props.candidate.vote_count || 0) === 0) return "No votes yet";
  return `${trendPercent.value}%`;
});

const initials = computed(() =>
  String(props.candidate.full_name || "")
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() || "")
    .join("")
);
</script>

<template>
  <article
    class="flex w-[168px] shrink-0 snap-start flex-col overflow-hidden rounded-card border border-border bg-white shadow-[0_1px_3px_0_rgb(15_23_42_/_0.06)] sm:w-[188px]"
  >
    <div class="relative aspect-[4/5] w-full overflow-hidden bg-surface-muted">
      <img
        v-if="photoUrl"
        :src="photoUrl"
        :alt="`${candidate.full_name} portrait`"
        class="h-full w-full object-cover object-[50%_18%]"
        loading="lazy"
      />
      <div
        v-else
        class="flex h-full w-full items-center justify-center bg-brand-50 text-lg font-bold text-brand-700"
      >
        {{ initials }}
      </div>

      <span
        v-if="isLive && candidate.rank && candidate.rank <= 3"
        class="absolute left-2 top-2 rounded-full bg-white/95 px-2 py-0.5 text-[10px] font-bold text-brand-800 shadow-sm"
      >
        #{{ candidate.rank }}
      </span>
    </div>

    <div class="flex flex-1 flex-col p-3">
      <p class="truncate text-sm font-semibold text-ink-primary">{{ candidate.full_name }}</p>
      <p class="mt-0.5 truncate text-xs text-ink-secondary">
        {{ candidate.position_title || "Candidate" }}
      </p>

      <div class="mt-3">
        <div class="flex items-center justify-between gap-2">
          <span class="text-[10px] font-semibold uppercase tracking-wide text-ink-secondary">
            Trend
          </span>
          <span
            class="text-xs font-bold tabular-nums"
            :class="isLive && trendPercent > 0 ? 'text-brand-700' : 'text-ink-secondary'"
          >
            {{ trendLabel }}
          </span>
        </div>
        <div class="mt-1.5 h-1.5 overflow-hidden rounded-full bg-surface-muted">
          <div
            class="h-full rounded-full bg-brand-600 transition-all duration-500 ease-out"
            :class="isLive ? '' : 'bg-slate-300'"
            :style="{ width: `${trendPercent}%` }"
          />
        </div>
      </div>
    </div>
  </article>
</template>
