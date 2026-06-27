<script setup>
import ProgressBar from "./ProgressBar.vue";

defineProps({
  steps: {
    type: Array,
    required: true,
  },
  currentStep: {
    type: Number,
    default: 0,
  },
});

const emit = defineEmits(["go-to"]);
</script>

<template>
  <nav aria-label="Voting progress" class="space-y-4">
    <ProgressBar
      :value="currentStep"
      :max="Math.max(steps.length - 1, 1)"
      :label="`Step ${currentStep + 1} of ${steps.length}`"
    />

    <ol class="flex flex-col gap-2 sm:flex-row sm:flex-wrap sm:gap-3">
      <li v-for="(step, index) in steps" :key="step.id || index" class="min-w-0 flex-1 sm:max-w-[12rem]">
        <button
          type="button"
          class="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-sm transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-600"
          :class="
            index === currentStep
              ? 'bg-brand-50 text-brand-800 ring-1 ring-brand-200'
              : index < currentStep
                ? 'bg-slate-50 text-slate-700 hover:bg-slate-100'
                : 'bg-white text-slate-500 ring-1 ring-slate-100'
          "
          :aria-current="index === currentStep ? 'step' : undefined"
          :disabled="index > currentStep"
          @click="index <= currentStep && emit('go-to', index)"
        >
          <span
            class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-semibold"
            :class="
              index < currentStep
                ? 'bg-brand-600 text-white'
                : index === currentStep
                  ? 'bg-brand-600 text-white'
                  : 'bg-slate-200 text-slate-600'
            "
          >
            {{ index + 1 }}
          </span>
          <span class="truncate font-medium">{{ step.label }}</span>
        </button>
      </li>
    </ol>
  </nav>
</template>
