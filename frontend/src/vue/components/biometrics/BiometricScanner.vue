<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from "vue";
import { useCamera } from "@/composables/useCamera";
import { useBiometricLiveness } from "@/composables/useFaceMesh";
import { buildProgressSteps } from "@/config/biometricProgressDisplay";
import { normalizeVerifyChallengeType } from "@/services/biometricChallengeManager";
import { drawScannerOverlay, faceStatusLabel } from "@/utils/biometricScannerOverlay";
import { bioDebug } from "@/utils/biometricDebug";
import { VButton } from "@/components/ui";

const props = defineProps({
  challenge: { type: Object, default: null },
  framesCaptured: { type: Number, default: 0 },
  framesRequired: { type: Number, default: 3 },
  mode: {
    type: String,
    default: "verify",
    validator: (v) => ["verify", "enrollment"].includes(v),
  },
  autoCapture: { type: Boolean, default: false },
});

const emit = defineEmits(["frame", "error", "challenge-complete"]);

const canvasRef = ref(null);
const initError = ref("");

const { videoRef, error: cameraError, isActive, start, stop, captureFrame } = useCamera({
  autoStart: false,
  highQuality: true,
});

const {
  loadingPhase,
  engineReady,
  cameraReady,
  landmarks,
  faceDetected,
  liveHint,
  warning,
  completedSteps,
  faceAligned,
  challengeComplete,
  initEngine,
  startLoop,
  stopLoop,
  pauseLoop,
  resumeLoop,
  resetChallengeTracking,
} = useBiometricLiveness();

const challengeType = computed(() => {
  if (props.mode === "enrollment") return "enrollment_sequence";
  const raw = props.challenge?.challenge_type || "";
  return props.mode === "verify" ? normalizeVerifyChallengeType(raw) : raw;
});

const progress = computed(() =>
  buildProgressSteps({
    completedSteps: completedSteps.value,
    challengeType: challengeType.value,
    mode: props.mode,
    framesCaptured: props.framesCaptured,
    framesRequired: props.framesRequired,
  })
);

const faceStatus = computed(() => {
  const faceStepDone = completedSteps.value.has("face");
  const hasFace = faceDetected.value || faceStepDone;
  // Once face step is complete, keep "Face detected" unless the face is truly lost.
  const alignedForBadge =
    faceAligned.value || (faceStepDone && hasFace && !warning.value.includes("Multiple"));
  return faceStatusLabel({
    hasFace,
    faceAligned: alignedForBadge,
    warning: warning.value,
  });
});

const loadingMessage = computed(() => {
  if (cameraError.value) return "";
  if (!isActive.value && loadingPhase.value === "idle") return "Starting camera…";
  if (!engineReady.value) return "Preparing secure scanner…";
  return "";
});

const friendlyCameraError = computed(() => {
  const msg = cameraError.value || initError.value;
  if (!msg) return "";
  if (/denied|permission/i.test(msg)) {
    return "Camera blocked — allow permission and retry.";
  }
  if (/not found|devices/i.test(msg)) {
    return "No camera found on this device.";
  }
  return "Unable to access camera.";
});

const statusLine = computed(() => {
  if (cameraError.value || initError.value) return "";
  if (loadingMessage.value) return loadingMessage.value;
  if (props.mode === "verify" && challengeComplete.value) {
    return props.framesCaptured >= props.framesRequired
      ? "Verification frames captured"
      : "Capturing verification frames…";
  }
  if (warning.value) return warning.value;
  return liveHint.value || "";
});

const captureLabel = computed(() => {
  const n = props.framesCaptured;
  const total = props.framesRequired;
  if (n > 0) return `Capture Frame ${n + 1} of ${total}`;
  return "Capture Verification Frame";
});

const canCapture = computed(() => {
  if (!challengeComplete.value || !faceAligned.value) return false;
  if (props.mode === "enrollment") {
    return (
      completedSteps.value.has("blink") &&
      completedSteps.value.has("turn_left") &&
      completedSteps.value.has("turn_right")
    );
  }
  return completedSteps.value.has("ready");
});

const showManualCapture = computed(() => props.mode === "enrollment" || !props.autoCapture);

watch(cameraError, (val) => {
  if (val) {
    bioDebug.error("camera_blocked", { message: val });
    emit("error", val);
  }
});

watch(
  () => props.challenge?.challenge_id,
  () => resetChallengeTracking()
);

function drawOverlay() {
  const canvas = canvasRef.value;
  const video = videoRef.value;
  if (!canvas || !video) return;

  const width = video.clientWidth;
  const height = video.clientHeight;
  if (!width || !height) return;

  if (canvas.width !== width || canvas.height !== height) {
    canvas.width = width;
    canvas.height = height;
  }

  const ctx = canvas.getContext("2d");
  drawScannerOverlay(ctx, {
    width,
    height,
    landmarks: landmarks.value,
    faceAligned: faceAligned.value,
  });
}

function handleVisibilityChange() {
  if (document.hidden) {
    pauseLoop();
  } else {
    resumeLoop();
    drawOverlay();
  }
}

function onLivenessComplete() {
  emit("challenge-complete");
}

async function bootstrap() {
  initError.value = "";
  stopLoop();

  try {
    if (!isActive.value) {
      await start();
      bioDebug.log("camera_started");
    }
    if (!engineReady.value) await initEngine();
    startLoop(videoRef, () => challengeType.value, {
      mode: () => props.mode,
      onFrame: drawOverlay,
      onChallengeComplete: onLivenessComplete,
    });
    drawOverlay();
  } catch (err) {
    initError.value = err?.message || "Scanner failed to start.";
    bioDebug.error("scanner_bootstrap_failed", { message: initError.value });
  }
}

function handleCapture() {
  if (!canCapture.value) return;
  const frame = captureFrame();
  if (frame) emit("frame", frame);
}

onMounted(() => {
  document.addEventListener("visibilitychange", handleVisibilityChange);
  bootstrap();
});

onUnmounted(() => {
  document.removeEventListener("visibilitychange", handleVisibilityChange);
  stopLoop();
  stop();
});

defineExpose({ captureFrame, start, stop, canCapture, challengeComplete });
</script>

<template>
  <div class="vb-bio-scanner" :class="{ 'vb-bio-scanner--verify': mode === 'verify' }">
    <div class="vb-bio-scanner__frame">
      <div class="vb-bio-scanner__viewport">
        <video
          ref="videoRef"
          class="vb-bio-scanner__video mirror"
          playsinline
          muted
          aria-label="Biometric camera preview"
        />
        <canvas ref="canvasRef" class="vb-bio-scanner__canvas mirror" aria-hidden="true" />

        <div
          class="vb-bio-scanner__status-badge"
          :class="`vb-bio-scanner__status-badge--${faceStatus.tone}`"
          role="status"
          aria-live="polite"
        >
          {{ faceStatus.text }}
        </div>

        <div
          v-if="friendlyCameraError || loadingMessage"
          class="vb-bio-scanner__loading"
        >
          <p v-if="friendlyCameraError" class="vb-bio-scanner__loading-error">{{ friendlyCameraError }}</p>
          <template v-else>
            <span class="vb-bio-scanner__spinner" aria-hidden="true" />
            <p>{{ loadingMessage }}</p>
          </template>
        </div>
      </div>
    </div>

    <p v-if="statusLine" class="vb-bio-scanner__status-line" role="status" aria-live="polite">
      {{ statusLine }}
    </p>

    <div class="vb-bio-scanner__progress" aria-label="Verification progress">
      <p class="vb-bio-scanner__progress-heading">
        Step {{ progress.current.index }} of {{ progress.total }}
      </p>

      <ul class="vb-bio-scanner__progress-list">
        <li
          v-for="step in progress.completed"
          :key="`done-${step.id}`"
          class="vb-bio-scanner__progress-item vb-bio-scanner__progress-item--done"
        >
          <span aria-hidden="true">✓</span>
          <span>{{ step.label }}</span>
        </li>
        <li
          v-if="progress.current && !progress.current.done"
          class="vb-bio-scanner__progress-item vb-bio-scanner__progress-item--active"
        >
          <span>{{ progress.current.label }}</span>
        </li>
      </ul>
    </div>

    <div v-if="showManualCapture" class="vb-bio-scanner__actions">
      <VButton
        type="button"
        variant="secondary"
        size="sm"
        block
        :disabled="!cameraReady || !canCapture"
        @click="handleCapture"
      >
        {{ captureLabel }}
      </VButton>
      <VButton v-if="!isActive || cameraError" type="button" variant="ghost" size="sm" @click="bootstrap">
        Retry camera
      </VButton>
    </div>
  </div>
</template>

<style scoped>
.mirror {
  transform: scaleX(-1);
}

.vb-bio-scanner {
  @apply flex w-full flex-col items-center gap-2;
}

.vb-bio-scanner--verify .vb-bio-scanner__frame {
  @apply max-w-[12rem];
}

.vb-bio-scanner--verify .vb-bio-scanner__viewport {
  @apply aspect-square;
}

.vb-bio-scanner--verify .vb-bio-scanner__status-line,
.vb-bio-scanner--verify .vb-bio-scanner__progress,
.vb-bio-scanner--verify .vb-bio-scanner__actions {
  @apply max-w-[12rem];
}

.vb-bio-scanner--verify .vb-bio-scanner__progress-heading {
  @apply text-[11px];
}

.vb-bio-scanner--verify .vb-bio-scanner__progress-list {
  @apply text-[10px];
}

.vb-bio-scanner--verify .vb-bio-scanner__status-line {
  @apply text-[11px];
}

.vb-bio-scanner--verify .vb-bio-scanner__status-badge {
  @apply left-2 top-2 px-2 py-0.5 text-[10px];
}

.vb-bio-scanner__frame {
  @apply relative w-full max-w-[20rem] rounded-card border border-border bg-slate-900 shadow-card;
}

.vb-bio-scanner__viewport {
  @apply relative aspect-[4/3] overflow-hidden rounded-card bg-slate-950;
}

.vb-bio-scanner__video,
.vb-bio-scanner__canvas {
  @apply absolute inset-0 h-full w-full object-cover;
}

.vb-bio-scanner__status-badge {
  @apply absolute left-3 top-3 z-10 rounded-md px-2.5 py-1 text-xs font-medium;
}

.vb-bio-scanner__status-badge--ok {
  @apply bg-success-700/90 text-white;
}

.vb-bio-scanner__status-badge--warning {
  @apply bg-warning-600/90 text-white;
}

.vb-bio-scanner__status-badge--lost {
  @apply bg-slate-700/90 text-slate-100;
}

.vb-bio-scanner__loading {
  @apply absolute inset-0 z-20 flex flex-col items-center justify-center gap-3 bg-slate-900/90 px-6 text-center text-sm text-slate-200;
}

.vb-bio-scanner__loading-error {
  @apply text-danger-600;
}

.vb-bio-scanner__spinner {
  @apply h-6 w-6 rounded-full border-2 border-slate-500 border-t-white;
  animation: vb-spin 0.8s linear infinite;
}

.vb-bio-scanner__status-line {
  @apply w-full max-w-[20rem] text-center text-sm font-medium text-slate-600;
}

.vb-bio-scanner__progress {
  @apply w-full max-w-[20rem] space-y-1;
}

.vb-bio-scanner__progress-heading {
  @apply text-sm font-semibold text-brand;
}

.vb-bio-scanner__progress-list {
  @apply space-y-1 text-sm text-slate-600;
}

.vb-bio-scanner__progress-item {
  @apply flex items-center gap-2;
}

.vb-bio-scanner__progress-item--done {
  @apply text-success-700;
}

.vb-bio-scanner__progress-item--active {
  @apply font-medium text-slate-800;
}

.vb-bio-scanner__actions {
  @apply flex w-full max-w-[20rem] items-center gap-2;
}

@keyframes vb-spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
