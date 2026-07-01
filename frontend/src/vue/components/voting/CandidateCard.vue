<script setup>
import { computed } from "vue";
import { getCandidatePhotoUrl } from "@/utils/candidateDisplay";
import CandidateInfoPanel from "@/components/candidates/CandidateInfoPanel.vue";

const props = defineProps({
  candidate: {
    type: Object,
    required: true,
  },
  positionTitle: { type: String, default: "" },
  selected: Boolean,
  disabled: Boolean,
  choiceType: {
    type: String,
    default: "single",
  },
  tabIndex: {
    type: Number,
    default: -1,
  },
  variant: {
    type: String,
    default: "default",
  },
});

const emit = defineEmits(["select", "keydown"]);

const isStudent = computed(() => props.variant === "student");
const photoUrl = computed(() => getCandidatePhotoUrl(props.candidate));

const ariaLabel = computed(
  () => `${props.candidate.full_name}${props.selected ? ", selected" : ""}`
);

function initials(name = "") {
  return name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() || "")
    .join("");
}
</script>

<template>
  <div
    v-if="isStudent"
    role="option"
    :aria-selected="selected"
    :aria-label="ariaLabel"
    :tabindex="tabIndex"
    class="vb-candidate-card group flex h-full min-w-0 cursor-pointer flex-col overflow-hidden rounded-lg border text-left transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-1 focus-visible:outline-brand-700"
    :class="[
      disabled ? 'cursor-not-allowed opacity-50' : '',
      selected
        ? 'border-brand-700 bg-surface shadow-sm ring-1 ring-brand-700/20'
        : 'border-border bg-surface hover:border-brand-300 hover:shadow-sm',
    ]"
    @click="!disabled && emit('select')"
    @keydown="emit('keydown', $event)"
  >
    <div class="vb-candidate-photo">
      <img
        v-if="photoUrl"
        :src="photoUrl"
        :alt="`${candidate.full_name} portrait`"
        class="vb-candidate-photo-img"
        loading="lazy"
      />
      <div
        v-else
        class="flex h-full w-full items-center justify-center bg-brand-50 text-lg font-bold text-brand-700"
      >
        {{ initials(candidate.full_name) }}
      </div>

      <div v-if="selected" class="absolute inset-0 bg-brand-900/10" aria-hidden="true" />

      <span
        class="absolute right-1.5 top-1.5 flex h-5 w-5 items-center justify-center rounded-full border shadow-sm transition"
        :class="
          selected
            ? 'border-brand-700 bg-brand-700 text-white'
            : 'border-white/90 bg-white/95 text-transparent group-hover:border-brand-400'
        "
        aria-hidden="true"
      >
        <svg v-if="selected" class="h-2.5 w-2.5" viewBox="0 0 12 12" fill="currentColor">
          <path d="M10.28 2.28a1 1 0 0 1 0 1.42l-5.5 5.5a1 1 0 0 1-1.42 0l-2.5-2.5a1 1 0 1 1 1.42-1.42L4.5 7.08l4.78-4.8a1 1 0 0 1 1.42 0z" />
        </svg>
      </span>
    </div>

    <CandidateInfoPanel :candidate="candidate" :position-title="positionTitle" />
  </div>

  <button
    v-else
    type="button"
    role="option"
    :aria-selected="selected"
    :aria-label="ariaLabel"
    :tabindex="tabIndex"
    :disabled="disabled"
    class="group flex w-full flex-col rounded-card border-2 p-5 text-left transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-700 disabled:cursor-not-allowed disabled:opacity-50"
    :class="
      selected
        ? 'border-brand-600 bg-brand-50 shadow-sm'
        : 'border-slate-200 bg-white hover:border-brand-300 hover:bg-slate-50'
    "
    @click="emit('select')"
    @keydown="emit('keydown', $event)"
  >
    <div class="flex items-start justify-between gap-3">
      <div class="min-w-0 flex-1">
        <p class="font-semibold text-slate-900">{{ candidate.full_name }}</p>
        <p v-if="candidate.department" class="mt-0.5 text-sm text-slate-500">
          {{ candidate.department }}
        </p>
      </div>
      <span
        class="flex h-5 w-5 shrink-0 items-center justify-center rounded-full border-2 transition"
        :class="
          selected
            ? 'border-brand-600 bg-brand-600 text-white'
            : 'border-slate-300 bg-white group-hover:border-brand-400'
        "
        aria-hidden="true"
      >
        <svg v-if="selected" class="h-3 w-3" viewBox="0 0 12 12" fill="currentColor">
          <path d="M10.28 2.28a1 1 0 0 1 0 1.42l-5.5 5.5a1 1 0 0 1-1.42 0l-2.5-2.5a1 1 0 1 1 1.42-1.42L4.5 7.08l4.78-4.8a1 1 0 0 1 1.42 0z" />
        </svg>
      </span>
    </div>
    <p v-if="candidate.manifesto" class="mt-3 line-clamp-3 text-sm text-slate-600">
      {{ candidate.manifesto }}
    </p>
  </button>
</template>
