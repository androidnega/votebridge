<script setup>
import { computed, onUnmounted, ref, watch } from "vue";

const props = defineProps({
  active: { type: Boolean, default: false },
  steps: {
    type: Array,
    default: () => [
      "Checking token…",
      "Validating…",
      "Almost ready…",
    ],
  },
  intervalMs: { type: Number, default: 600 },
});

const stepIndex = ref(0);
let timer = null;

const currentStep = computed(() => props.steps[stepIndex.value] || props.steps[0]);

function clearTimer() {
  if (timer) {
    window.clearInterval(timer);
    timer = null;
  }
}

function startSequence() {
  clearTimer();
  stepIndex.value = 0;
  timer = window.setInterval(() => {
    if (stepIndex.value < props.steps.length - 1) {
      stepIndex.value += 1;
    }
  }, props.intervalMs);
}

watch(
  () => props.active,
  (running) => {
    if (running) startSequence();
    else clearTimer();
  },
  { immediate: true }
);

onUnmounted(clearTimer);
</script>

<template>
  <section
    class="w-full rounded-card border border-border bg-surface px-6 py-14 shadow-card sm:px-8"
    role="status"
    aria-live="polite"
    aria-busy="true"
  >
    <div class="mx-auto flex max-w-sm flex-col items-center text-center">
      <div
        class="mb-5 h-9 w-9 animate-spin rounded-full border-2 border-brand-200 border-t-brand-700"
        aria-hidden="true"
      />
      <p class="text-sm font-medium text-ink-primary">{{ currentStep }}</p>
      <p class="mt-1.5 text-xs text-ink-secondary">This only takes a moment</p>
    </div>
  </section>
</template>
