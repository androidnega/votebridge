<script setup>
import { BLINK_EAR_CLOSED_THRESHOLD } from "@/utils/blinkDetection";

defineProps({
  metrics: {
    type: Object,
    default: () => ({}),
  },
});

const show = import.meta.env.DEV;
</script>

<template>
  <div v-if="show" class="vb-bio-dev-overlay" aria-hidden="true">
    <p>Left EAR: {{ metrics.leftEar != null ? metrics.leftEar.toFixed(2) : "—" }}</p>
    <p>Right EAR: {{ metrics.rightEar != null ? metrics.rightEar.toFixed(2) : "—" }}</p>
    <p>Blink Threshold: {{ BLINK_EAR_CLOSED_THRESHOLD.toFixed(2) }}</p>
    <p>Blink Counter: {{ metrics.blinkCount ?? 0 }}</p>
    <p>Face Confidence: {{ metrics.faceConfidence != null ? metrics.faceConfidence.toFixed(2) : "—" }}</p>
    <p>Challenge: {{ metrics.challenge || "—" }}</p>
    <p v-if="metrics.phase">Phase: {{ metrics.phase }}</p>
  </div>
</template>

<style scoped>
.vb-bio-dev-overlay {
  @apply pointer-events-none absolute bottom-0 left-0 right-0 z-30 bg-slate-950/80 px-1.5 py-1 font-mono text-[8px] leading-tight text-emerald-300;
}
</style>
