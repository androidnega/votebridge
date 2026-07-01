<script setup>
import { parseCandidateMeta } from "@/utils/candidateDisplay";

defineProps({
  candidate: { type: Object, required: true },
});

const emit = defineEmits(["select"]);

function initials(name = "") {
  return name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() || "")
    .join("");
}

function meta(candidate) {
  return parseCandidateMeta(candidate.manifesto, candidate.department);
}
</script>

<template>
  <button
    type="button"
    class="flex w-full min-h-[44px] flex-col rounded-card border border-border bg-surface p-4 text-left shadow-card transition hover:border-brand-200 hover:shadow-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500"
    @click="emit('select', candidate)"
  >
    <div class="flex items-start gap-4">
      <div
        class="flex h-16 w-16 shrink-0 items-center justify-center overflow-hidden rounded-input bg-brand-50 text-lg font-bold text-brand-700"
        aria-hidden="true"
      >
        <img
          v-if="candidate.image_url"
          :src="candidate.image_url"
          :alt="`${candidate.full_name} photo`"
          class="h-full w-full object-cover"
        />
        <span v-else>{{ initials(candidate.full_name) }}</span>
      </div>
      <div class="min-w-0 flex-1">
        <p class="text-base font-semibold text-slate-900">{{ candidate.full_name }}</p>
        <p class="mt-0.5 text-sm font-medium text-brand-700">{{ candidate.position_title }}</p>
        <p v-if="meta(candidate).faculty" class="mt-1 text-xs text-slate-600">
          {{ meta(candidate).faculty }}
        </p>
        <p v-if="meta(candidate).department" class="text-xs text-slate-500">
          {{ meta(candidate).department }}
        </p>
      </div>
    </div>
    <p v-if="meta(candidate).manifestoSummary" class="mt-3 line-clamp-3 text-sm leading-relaxed text-slate-600">
      {{ meta(candidate).manifestoSummary }}
    </p>
  </button>
</template>
