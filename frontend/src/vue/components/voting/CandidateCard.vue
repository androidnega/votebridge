<script setup>
import { computed } from "vue";

const props = defineProps({
  candidate: {
    type: Object,
    required: true,
  },
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
});

const emit = defineEmits(["select", "keydown"]);

const ariaLabel = computed(
  () => `${props.candidate.full_name}${props.selected ? ", selected" : ""}`
);
</script>

<template>
  <button
    type="button"
    role="option"
    :aria-selected="selected"
    :aria-label="ariaLabel"
    :tabindex="tabIndex"
    :disabled="disabled"
    class="group flex w-full flex-col rounded-xl border-2 p-4 text-left transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-600 disabled:cursor-not-allowed disabled:opacity-50"
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
