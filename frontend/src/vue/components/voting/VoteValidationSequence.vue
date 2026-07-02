<script setup>
import { computed, onUnmounted, ref, watch } from "vue";
import { FaIcon } from "@/components/ui";

const props = defineProps({
  active: { type: Boolean, default: false },
  success: { type: Boolean, default: false },
  steps: {
    type: Array,
    default: () => ["Checking token…", "Validating…", "Almost ready…"],
  },
  intervalMs: { type: Number, default: 650 },
  hint: { type: String, default: "This only takes a moment" },
  successTitle: { type: String, default: "Verified" },
  successText: { type: String, default: "Continuing…" },
});

const stepIndex = ref(0);
let timer = null;

const currentStep = computed(() => props.steps[stepIndex.value] || props.steps[0]);
const completedCount = computed(() =>
  props.success ? props.steps.length : Math.max(0, stepIndex.value)
);

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
    if (running && !props.success) startSequence();
    else clearTimer();
  },
  { immediate: true }
);

watch(
  () => props.success,
  (done) => {
    if (done) {
      clearTimer();
      stepIndex.value = props.steps.length - 1;
    }
  }
);

onUnmounted(clearTimer);
</script>

<template>
  <section
    class="vb-vote-validate w-full"
    role="status"
    :aria-live="success ? 'polite' : 'assertive'"
    :aria-busy="active && !success"
  >
    <div v-if="success" class="vb-vote-validate-success-icon" aria-hidden="true">
      <FaIcon icon="fa-circle-check" class="text-3xl text-success-600" />
    </div>
    <div v-else class="vb-vote-validate-ring" aria-hidden="true">
      <div class="vb-vote-validate-ring-inner" />
    </div>

    <Transition name="vb-step-label" mode="out-in">
      <p v-if="success" key="success-title" class="vb-vote-validate-status">
        {{ successTitle }}
      </p>
      <p v-else key="step-label" class="vb-vote-validate-status">
        {{ currentStep }}
      </p>
    </Transition>

    <p class="mt-1.5 text-xs text-ink-secondary">
      {{ success ? successText : hint }}
    </p>

    <ul class="vb-vote-validate-checklist" aria-hidden="true">
      <li
        v-for="(step, index) in steps"
        :key="step"
        class="vb-vote-validate-checklist-item"
        :class="{
          'is-done': index < completedCount || success,
          'is-current': index === stepIndex && active && !success,
        }"
      >
        <span class="vb-vote-validate-checklist-dot">
          <FaIcon v-if="index < completedCount || success" icon="fa-check" class="text-[10px]" />
        </span>
        <span class="truncate">{{ step.replace(/…$/, "") }}</span>
      </li>
    </ul>
  </section>
</template>
