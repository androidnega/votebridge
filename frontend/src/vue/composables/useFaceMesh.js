import { onUnmounted, ref, shallowRef } from "vue";
import {
  BLINK_EAR_CLOSED_THRESHOLD,
  BLINK_EAR_OPEN_THRESHOLD,
  createBlinkDetector,
} from "@/utils/blinkDetection";
import {
  estimateLighting,
  faceCenterOffset,
  headYaw,
  isFaceInsideGuide,
  isFaceLargeEnough,
} from "@/utils/faceDetectionUtils";
import { detectFaceSnapshot, getFaceLandmarker } from "@/services/faceLandmarkerEngine";
import {
  challengeNeeds,
  getRequiredSteps,
  isChallengeComplete,
  nextActionHint,
} from "@/services/biometricChallengeManager";
import { bioDebug } from "@/utils/biometricDebug";

const DETECT_GAP_MS = 120;
const DETECT_GAP_BLINK_MS = 66;
const DETECT_IDLE_GAP_MS = 2000;
const LIGHTING_INTERVAL_MS = 3000;
const YAW_LEFT_MARK = 0.32;
const YAW_RIGHT_MARK = -0.32;

export function useBiometricLiveness() {
  const loadingPhase = ref("idle");
  const engineReady = ref(false);
  const cameraReady = ref(false);
  const landmarks = shallowRef(null);
  const faceDetected = ref(false);
  const liveHint = ref("");
  const warning = ref("");
  const completedSteps = ref(new Set());
  const faceAligned = ref(false);
  const challengeComplete = ref(false);

  let detectTimer = null;
  let inFlight = false;
  let lastLightingAt = 0;
  let loopPaused = false;
  let loopStopped = false;
  let videoRefForLoop = null;
  let challengeTypeFn = null;
  let modeFn = null;
  let onFrameCallback = null;
  let onChallengeComplete = null;
  let cachedLighting = { level: "ok", score: 0.5 };
  let hadFace = false;
  const blinkDetector = createBlinkDetector();

  async function initEngine() {
    loadingPhase.value = "detection";
    await getFaceLandmarker();
    engineReady.value = true;
    loadingPhase.value = "ready";
  }

  function resolveChallengeType() {
    if (typeof challengeTypeFn === "function") return challengeTypeFn();
    return challengeTypeFn?.value ?? "";
  }

  function resolveMode() {
    if (typeof modeFn === "function") return modeFn();
    return modeFn?.value ?? "verify";
  }

  function resetChallengeTracking() {
    blinkDetector.reset();
    hadFace = false;
    warning.value = "";
    challengeComplete.value = false;
    completedSteps.value = new Set();
  }

  function setHint(msg) {
    if (liveHint.value !== msg) liveHint.value = msg;
  }

  function setWarning(msg) {
    if (warning.value !== msg) warning.value = msg;
  }

  function markStep(id) {
    if (!id || completedSteps.value.has(id)) return;
    const next = new Set(completedSteps.value);
    next.add(id);
    completedSteps.value = next;
    bioDebug.log(`step_${id}`);
  }

  function trackBlink(pts, type, mode, now) {
    if (!challengeNeeds(type, "blink", mode)) return;

    const offsetY = faceCenterOffset(pts).offsetY;
    const result = blinkDetector.update(pts, { yaw: headYaw(pts), offsetY }, now);

    bioDebug.metrics("ear_frame", {
      left: result.left.toFixed(2),
      right: result.right.toFixed(2),
      threshold: BLINK_EAR_CLOSED_THRESHOLD,
      open: BLINK_EAR_OPEN_THRESHOLD,
      phase: result.phase,
    });

    if (result.blinked) {
      bioDebug.log("blink_detected", { count: result.count });
      markStep(result.count >= 2 ? "blink2" : "blink");
    }
  }

  function trackHeadTurn(yaw, type, mode) {
    if (mode !== "enrollment") return;
    if (challengeNeeds(type, "turn_left", mode) && yaw >= YAW_LEFT_MARK) {
      markStep("turn_left");
    }
    if (challengeNeeds(type, "turn_right", mode) && yaw <= YAW_RIGHT_MARK) {
      markStep("turn_right");
    }
  }

  function detectGapFor(type, mode) {
    if (!challengeNeeds(type, "blink", mode)) return DETECT_GAP_MS;
    if (type === "blink_twice" && completedSteps.value.has("blink2")) return DETECT_GAP_MS;
    if (completedSteps.value.has("blink") && type !== "blink_twice") return DETECT_GAP_MS;
    return DETECT_GAP_BLINK_MS;
  }

  function analyzeFrame(video, challengeType, mode, checkLighting) {
    const result = detectFaceSnapshot(video);
    if (!result) return;

    const type = challengeType || "";
    const count = result.faceLandmarks?.length || 0;
    const now = performance.now();

    if (count === 0) {
      landmarks.value = null;
      faceDetected.value = false;
      faceAligned.value = false;
      if (hadFace) bioDebug.log("face_lost");
      hadFace = false;
      setWarning("");
      setHint("Position your face in the frame");
      return;
    }

    if (count > 1) {
      setWarning("Multiple faces detected");
      bioDebug.warn("multiple_faces");
    } else {
      setWarning("");
    }

    const pts = result.faceLandmarks[0];
    landmarks.value = pts;
    faceDetected.value = true;

    if (!hadFace) {
      bioDebug.log("face_detected");
      hadFace = true;
    }

    markStep("face");
    trackBlink(pts, type, mode, now);
    trackHeadTurn(headYaw(pts), type, mode);

    if (checkLighting) {
      cachedLighting = estimateLighting(video);
      lastLightingAt = performance.now();
    }

    if (cachedLighting.level === "low") {
      setWarning("Improve lighting");
      faceAligned.value = false;
    } else if (!isFaceLargeEnough(pts)) {
      faceAligned.value = false;
      setHint("Move closer to the camera");
    } else if (!isFaceInsideGuide(pts)) {
      setWarning("Center your face in the frame");
      faceAligned.value = false;
    } else {
      if (!warning.value.includes("Multiple")) setWarning("");
      faceAligned.value = true;
    }

    const complete = isChallengeComplete(type, completedSteps.value, mode);
    if (complete && faceAligned.value && !challengeComplete.value) {
      markStep("ready");
      challengeComplete.value = true;
      bioDebug.log("challenge_completed", { type, mode });
      onChallengeComplete?.();
    }

    setHint(nextActionHint(type, completedSteps.value, warning.value, mode));
  }

  function clearDetectTimer() {
    if (detectTimer) {
      clearTimeout(detectTimer);
      detectTimer = null;
    }
  }

  function scheduleNextTick(delay) {
    clearDetectTimer();
    if (loopStopped) return;
    detectTimer = setTimeout(runDetectionTick, delay);
  }

  function runDetectionTick() {
    if (loopStopped || loopPaused || inFlight) return;

    const video = videoRefForLoop?.value;
    if (!video || !engineReady.value) {
      scheduleNextTick(DETECT_GAP_MS);
      return;
    }

    if (video.readyState >= 2) {
      cameraReady.value = true;
      markStep("camera");
    }

    if (challengeComplete.value) {
      scheduleNextTick(DETECT_IDLE_GAP_MS);
      onFrameCallback?.();
      return;
    }

    inFlight = true;
    const started = performance.now();
    const type = resolveChallengeType();
    const mode = resolveMode();

    requestAnimationFrame(() => {
      try {
        const now = performance.now();
        const checkLighting = now - lastLightingAt >= LIGHTING_INTERVAL_MS;
        analyzeFrame(video, type, mode, checkLighting);
        onFrameCallback?.();
      } finally {
        inFlight = false;
        if (!loopStopped && !loopPaused) {
          const elapsed = performance.now() - started;
          const nextGap = detectGapFor(resolveChallengeType(), resolveMode());
          scheduleNextTick(Math.max(nextGap, elapsed + 16));
        }
      }
    });
  }

  function startLoop(videoRef, challengeTypeRef, { mode, onFrame, onChallengeComplete: onComplete } = {}) {
    stopLoop();
    videoRefForLoop = videoRef;
    challengeTypeFn = challengeTypeRef;
    modeFn = mode ?? (() => "verify");
    onFrameCallback = onFrame;
    onChallengeComplete = onComplete ?? null;
    loopPaused = false;
    loopStopped = false;
    scheduleNextTick(0);
  }

  function stopLoop() {
    loopStopped = true;
    clearDetectTimer();
    inFlight = false;
    onFrameCallback = null;
    onChallengeComplete = null;
    cameraReady.value = false;
  }

  function pauseLoop() {
    loopPaused = true;
    clearDetectTimer();
  }

  function resumeLoop() {
    if (loopStopped) return;
    loopPaused = false;
    if (!inFlight && !detectTimer) {
      scheduleNextTick(0);
    }
  }

  onUnmounted(() => {
    stopLoop();
  });

  return {
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
    getRequiredSteps: () => getRequiredSteps(resolveChallengeType(), resolveMode()),
  };
}

/** @deprecated Use useBiometricLiveness */
export function useFaceMesh() {
  return useBiometricLiveness();
}
