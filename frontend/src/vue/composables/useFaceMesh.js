import { onUnmounted, ref, shallowRef } from "vue";
import { createBlinkDetector } from "@/utils/blinkDetection";
import {
  ENROLL_MIN_FACE_WIDTH,
  estimateLighting,
  faceCenterOffset,
  headYaw,
  isFaceInsideGuide,
  isFaceLargeEnough,
  isValidLandmarkSet,
  normalizeLandmarkSet,
  VERIFY_MIN_FACE_WIDTH,
} from "@/utils/faceDetectionUtils";
import { detectFaceSnapshot, getFaceLandmarker } from "@/services/faceLandmarkerEngine";
import {
  challengeNeeds,
  getRequiredSteps,
  isChallengeComplete,
  nextActionHint,
  normalizeVerifyChallengeType,
} from "@/services/biometricChallengeManager";
import { bioDebug } from "@/utils/biometricDebug";
import { createSignalStabilizer } from "@/utils/signalStabilizer";

const DETECT_GAP_MS = 120;
const DETECT_GAP_BLINK_MS = 80;
const DETECT_IDLE_GAP_MS = 2000;
const LIGHTING_INTERVAL_MS = 3000;
const LANDMARK_HOLD_MS = 900;
const YAW_LEFT_MARK = 0.32;
const YAW_RIGHT_MARK = -0.32;
const FACE_STABLE_ENTER = 3;
const FACE_STABLE_EXIT = 12;
const ALIGNED_STABLE_ENTER = 3;
const ALIGNED_STABLE_EXIT = 8;

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
  let hadStableFace = false;
  let lastGoodLandmarks = null;
  let lastGoodLandmarksAt = 0;
  const facePresence = createSignalStabilizer({
    enterCount: FACE_STABLE_ENTER,
    exitCount: FACE_STABLE_EXIT,
  });
  const faceAlignment = createSignalStabilizer({
    enterCount: ALIGNED_STABLE_ENTER,
    exitCount: ALIGNED_STABLE_EXIT,
  });
  let blinkDetector = createBlinkDetector({ profile: "verify" });

  function rebuildBlinkDetector() {
    const profile = resolveMode() === "verify" ? "verify" : "enrollment";
    blinkDetector = createBlinkDetector({ profile });
  }

  async function initEngine() {
    loadingPhase.value = "detection";
    await getFaceLandmarker();
    engineReady.value = true;
    loadingPhase.value = "ready";
  }

  function resolveChallengeType() {
    const raw = typeof challengeTypeFn === "function" ? challengeTypeFn() : challengeTypeFn?.value ?? "";
    if (resolveMode() === "verify") return normalizeVerifyChallengeType(raw);
    return raw;
  }

  function resolveMode() {
    if (typeof modeFn === "function") return modeFn();
    return modeFn?.value ?? "verify";
  }

  function resetChallengeTracking() {
    rebuildBlinkDetector();
    facePresence.reset();
    faceAlignment.reset();
    hadStableFace = false;
    lastGoodLandmarks = null;
    lastGoodLandmarksAt = 0;
    faceDetected.value = false;
    faceAligned.value = false;
    landmarks.value = null;
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
      min: result.min.toFixed(2),
      baseline: result.baseline ? result.baseline.toFixed(2) : null,
      closeAt: result.closeAt ? result.closeAt.toFixed(2) : null,
      openAt: result.openAt ? result.openAt.toFixed(2) : null,
      phase: result.phase,
    });

    if (result.blinked) {
      bioDebug.log("blink_detected", { count: result.count });
      markStep(result.count >= 2 ? "blink2" : "blink");
    } else if (result.rejected) {
      bioDebug.metrics("blink_rejected", { reason: result.rejected, phase: result.phase });
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

  function evaluateRawAlignment(pts, mode) {
    if (!isValidLandmarkSet(pts)) return false;
    const minWidth = mode === "verify" ? VERIFY_MIN_FACE_WIDTH : ENROLL_MIN_FACE_WIDTH;
    if (!isFaceLargeEnough(pts, { minWidth })) return false;
    if (mode === "verify") return true;
    if (cachedLighting.level === "low") return false;
    return isFaceInsideGuide(pts, { relaxed: false });
  }

  function alignmentHint(pts, mode) {
    if (mode !== "verify" && cachedLighting.level === "low") {
      return { warning: "Improve lighting", hint: "Improve lighting" };
    }
    const minWidth = mode === "verify" ? VERIFY_MIN_FACE_WIDTH : ENROLL_MIN_FACE_WIDTH;
    if (!isFaceLargeEnough(pts, { minWidth })) {
      return { warning: "", hint: "Move closer to the camera" };
    }
    if (mode !== "verify" && !isFaceInsideGuide(pts, { relaxed: false })) {
      return { warning: "Center your face in the frame", hint: "Center your face in the frame" };
    }
    if (mode === "verify" && cachedLighting.level === "low") {
      return { warning: "Improve lighting", hint: "Blink now — more light helps" };
    }
    return { warning: "", hint: "Position your face in the frame" };
  }

  function analyzeFrame(video, challengeType, mode, checkLighting) {
    const result = detectFaceSnapshot(video);
    if (!result) return;

    const type = challengeType || "";
    const count = result.faceLandmarks?.length || 0;
    const now = performance.now();
    const rawHasFace = count > 0;

    let pts = null;
    if (rawHasFace) {
      const candidate = normalizeLandmarkSet(result.faceLandmarks[0]);
      if (candidate) {
        pts = candidate;
        lastGoodLandmarks = candidate;
        lastGoodLandmarksAt = now;
      }
    } else if (
      isValidLandmarkSet(lastGoodLandmarks) &&
      now - lastGoodLandmarksAt < LANDMARK_HOLD_MS
    ) {
      pts = lastGoodLandmarks;
    }

    const faceStable = facePresence.update(isValidLandmarkSet(pts));
    faceDetected.value = faceStable;

    if (pts && (rawHasFace || faceStable)) {
      landmarks.value = pts;
    } else if (!faceStable) {
      landmarks.value = null;
    }

    if (!faceStable) {
      faceAlignment.update(false);
      faceAligned.value = false;
      if (hadStableFace) bioDebug.log("face_lost");
      hadStableFace = false;
      setWarning("");
      setHint("Position your face in the frame");
      return;
    }

    if (!isValidLandmarkSet(pts)) {
      faceAlignment.update(false);
      faceAligned.value = false;
      setHint("Position your face in the frame");
      return;
    }

    if (!hadStableFace) {
      bioDebug.log("face_detected");
      hadStableFace = true;
    }

    markStep("face");

    if (count > 1) {
      setWarning("Multiple faces detected");
      bioDebug.warn("multiple_faces");
    } else {
      setWarning("");
    }

    if (checkLighting) {
      cachedLighting = estimateLighting(video);
      lastLightingAt = performance.now();
    }

    const rawAligned = evaluateRawAlignment(pts, mode);
    const alignedStable = faceAlignment.update(rawAligned);
    const readyForLiveness = mode === "verify" ? rawAligned : alignedStable;
    faceAligned.value = readyForLiveness;

    if (!readyForLiveness) {
      const guidance = alignmentHint(pts, mode);
      setWarning(guidance.warning);
      setHint(guidance.hint);
    } else {
      if (!warning.value.includes("Multiple")) setWarning("");
      trackBlink(pts, type, mode, now);
      trackHeadTurn(headYaw(pts), type, mode);
    }

    const complete = isChallengeComplete(type, completedSteps.value, mode);
    if (complete && readyForLiveness && !challengeComplete.value) {
      markStep("ready");
      challengeComplete.value = true;
      bioDebug.log("challenge_completed", { type, mode });
      onChallengeComplete?.();
    }

    if (readyForLiveness) {
      setHint(nextActionHint(type, completedSteps.value, warning.value, mode));
    }
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
      } catch (err) {
        bioDebug.error("analyze_frame_failed", { message: err?.message });
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
    rebuildBlinkDetector();
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
