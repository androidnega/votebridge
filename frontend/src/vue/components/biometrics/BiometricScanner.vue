<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from "vue";
import { useCamera } from "@/composables/useCamera";
import { useFaceMesh } from "@/composables/useFaceMesh";
import { buildProgressSteps } from "@/config/biometricProgressDisplay";
import { faceBoundingBox, MESH_CONNECTIONS } from "@/utils/faceDetectionUtils";
import { bioDebug } from "@/utils/biometricDebug";
import { VButton } from "@/components/ui";
import BiometricDevOverlay from "@/components/biometrics/BiometricDevOverlay.vue";

const props = defineProps({
  challenge: { type: Object, default: null },
  framesCaptured: { type: Number, default: 0 },
  framesRequired: { type: Number, default: 3 },
  mode: {
    type: String,
    default: "verify",
    validator: (v) => ["verify", "enrollment"].includes(v),
  },
});

const emit = defineEmits(["frame", "error"]);

const canvasRef = ref(null);
const initError = ref("");
const showDevOverlay = import.meta.env.DEV;

const { videoRef, error: cameraError, isActive, start, stop, captureFrame } = useCamera({
  autoStart: false,
});

const {
  loadingPhase,
  engineReady,
  cameraReady,
  landmarks,
  liveHint,
  warning,
  completedSteps,
  blinkHighlight,
  faceAligned: meshFaceAligned,
  blinkMetrics,
  initEngine,
  startLoop,
  stopLoop,
  pauseLoop,
  resumeLoop,
  resetChallengeTracking,
} = useFaceMesh();

const challengeType = computed(() => {
  if (props.mode === "enrollment") return "enrollment_sequence";
  return props.challenge?.challenge_type || "";
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

const loadingMessage = computed(() => {
  if (cameraError.value) return "";
  if (!isActive.value && loadingPhase.value === "idle") return "Starting camera…";
  if (loadingPhase.value === "engine") return "Loading scanner…";
  if (loadingPhase.value === "detection") return "Preparing detection…";
  if (!engineReady.value) return "Initializing…";
  return "";
});

const faceAligned = computed(() => meshFaceAligned.value);

const statusLine = computed(() => {
  if (cameraError.value || initError.value) return "";
  if (loadingMessage.value && !engineReady.value) return loadingMessage.value;
  if (warning.value) return warning.value;
  if (engineReady.value && liveHint.value) return liveHint.value;
  return "";
});

const captureLabel = computed(() => {
  const n = props.framesCaptured;
  const total = props.framesRequired;
  if (n > 0) return `Capture Frame ${n + 1} of ${total}`;
  return "Capture Verification Frame";
});

const canCapture = computed(() => {
  if (props.mode === "enrollment") {
    return (
      completedSteps.value.has("blink") &&
      completedSteps.value.has("turn_left") &&
      completedSteps.value.has("turn_right")
    );
  }
  return completedSteps.value.has("ready");
});

const friendlyCameraError = computed(() => {
  const msg = cameraError.value || initError.value;
  if (!msg) return "";
  if (/denied|permission/i.test(msg)) {
    return "Camera blocked — allow permission and tap Retry.";
  }
  if (/not found|devices/i.test(msg)) {
    return "No camera found on this device.";
  }
  return "Unable to access camera.";
});

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

function drawMesh(ctx, pts, width, height, aligned) {
  const color = aligned ? "rgba(46, 125, 50, 0.35)" : "rgba(255, 255, 255, 0.18)";
  ctx.strokeStyle = color;
  ctx.lineWidth = 1;

  const drawPaths = (paths) => {
    for (const [a, b] of paths) {
      const p1 = pts[a];
      const p2 = pts[b];
      if (!p1 || !p2) continue;
      ctx.beginPath();
      ctx.moveTo(p1.x * width, p1.y * height);
      ctx.lineTo(p2.x * width, p2.y * height);
      ctx.stroke();
    }
  };

  drawPaths(MESH_CONNECTIONS.faceOval);
  drawPaths(MESH_CONNECTIONS.leftEye);
  drawPaths(MESH_CONNECTIONS.rightEye);
}

function drawGuideOverlays(ctx, width, height, aligned) {
  const cx = width / 2;
  const cy = height * 0.46;
  ctx.save();
  ctx.strokeStyle = aligned ? "rgba(46, 125, 50, 0.45)" : "rgba(255,255,255,0.25)";
  ctx.lineWidth = 1;
  ctx.setLineDash(aligned ? [] : [5, 4]);
  ctx.beginPath();
  ctx.ellipse(cx, cy, width * 0.28, height * 0.36, 0, 0, Math.PI * 2);
  ctx.stroke();
  ctx.setLineDash([]);
  ctx.restore();
}

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
  ctx.clearRect(0, 0, width, height);

  const aligned = faceAligned.value;
  drawGuideOverlays(ctx, width, height, aligned);

  const pts = landmarks.value;
  if (!pts) return;

  drawMesh(ctx, pts, width, height, aligned);

  const box = faceBoundingBox(pts);
  ctx.strokeStyle = aligned ? "rgba(22, 163, 74, 0.85)" : "rgba(217, 119, 6, 0.75)";
  ctx.lineWidth = 1;
  ctx.strokeRect(box.minX * width, box.minY * height, box.width * width, box.height * height);
}

function handleVisibilityChange() {
  if (document.hidden) {
    pauseLoop();
  } else {
    resumeLoop();
    drawOverlay();
  }
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
    startLoop(videoRef, () => challengeType.value, { onFrame: drawOverlay });
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

defineExpose({ captureFrame, start, stop });
</script>

<template>
  <div class="vb-bio-scanner">
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

        <BiometricDevOverlay v-if="showDevOverlay" :metrics="blinkMetrics" />

        <div
          v-if="friendlyCameraError || (loadingMessage && !engineReady)"
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

    <div class="vb-bio-scanner__actions">
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
        Retry
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

.vb-bio-scanner__frame {
  @apply relative w-full max-w-[12rem] rounded-card border border-border bg-slate-900 shadow-card;
}

.vb-bio-scanner__viewport {
  @apply relative aspect-square overflow-hidden rounded-card bg-slate-950;
}

.vb-bio-scanner__video,
.vb-bio-scanner__canvas {
  @apply absolute inset-0 h-full w-full object-cover;
}

.vb-bio-scanner__loading {
  @apply absolute inset-0 z-20 flex flex-col items-center justify-center gap-2 bg-slate-900/90 px-3 text-center text-[11px] text-slate-200;
}

.vb-bio-scanner__loading-error {
  @apply text-danger-600;
}

.vb-bio-scanner__spinner {
  @apply h-4 w-4 rounded-full border-2 border-slate-500 border-t-white;
  animation: vb-spin 0.8s linear infinite;
}

.vb-bio-scanner__status-line {
  @apply w-full max-w-[12rem] truncate text-center text-[11px] font-medium text-slate-600;
}

.vb-bio-scanner__progress {
  @apply w-full max-w-[12rem] space-y-1;
}

.vb-bio-scanner__progress-heading {
  @apply text-[11px] font-semibold text-brand;
}

.vb-bio-scanner__progress-list {
  @apply space-y-0.5 text-[10px] text-slate-600;
}

.vb-bio-scanner__progress-item {
  @apply flex items-center gap-1.5;
}

.vb-bio-scanner__progress-item--done {
  @apply text-success-700;
}

.vb-bio-scanner__progress-item--active {
  @apply font-medium text-slate-700;
}

.vb-bio-scanner__actions {
  @apply flex w-full max-w-[12rem] items-center gap-1.5;
}

@keyframes vb-spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
