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
import { bioDebug } from "@/utils/biometricDebug";

/** ~8 samples/sec default; faster during blink challenges to catch short blinks. */
const DETECT_GAP_MS = 120;
const DETECT_GAP_BLINK_MS = 66;
const DETECT_IDLE_GAP_MS = 2000;
const LIGHTING_INTERVAL_MS = 3000;
const YAW_LEFT_MARK = 0.32;
const YAW_RIGHT_MARK = -0.32;

function estimateFaceConfidence(landmarks) {
  if (!landmarks?.length) return 0;
  const pts = landmarks;
  const withVis = pts.filter((p) => p?.visibility != null);
  if (withVis.length) {
    return withVis.reduce((sum, p) => sum + (p.visibility ?? 0), 0) / withVis.length;
  }
  return 1;
}

export function useFaceMesh() {
  const loadingPhase = ref("idle");
  const engineReady = ref(false);
  const cameraReady = ref(false);
  const landmarks = shallowRef(null);
  const liveHint = ref("");
  const warning = ref("");
  const completedSteps = ref(new Set());
  const blinkHighlight = ref(false);
  const faceAligned = ref(false);
  const blinkMetrics = ref({
    leftEar: null,
    rightEar: null,
    blinkCount: 0,
    faceConfidence: 0,
    challenge: "",
    phase: "open",
  });

  let detectTimer = null;
  let inFlight = false;
  let lastLightingAt = 0;
  let blinkHighlightTimer = null;
  let loopPaused = false;
  let loopStopped = false;
  let videoRefForLoop = null;
  let challengeTypeFn = null;
  let onFrameCallback = null;
  let cachedLighting = { level: "ok", score: 0.5 };
  let hadFace = false;
  const blinkDetector = createBlinkDetector();

  async function initEngine() {
    loadingPhase.value = "engine";
    loadingPhase.value = "detection";
    await getFaceLandmarker();
    engineReady.value = true;
    loadingPhase.value = "ready";
  }

  function resetChallengeTracking() {
    blinkDetector.reset();
    hadFace = false;
    blinkHighlight.value = false;
    warning.value = "";
    blinkMetrics.value = {
      leftEar: null,
      rightEar: null,
      blinkCount: 0,
      faceConfidence: 0,
      challenge: resolveChallengeType(),
      phase: "open",
    };
    if (blinkHighlightTimer) {
      clearTimeout(blinkHighlightTimer);
      blinkHighlightTimer = null;
    }
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

  function triggerBlinkHighlight() {
    blinkHighlight.value = true;
    if (blinkHighlightTimer) clearTimeout(blinkHighlightTimer);
    blinkHighlightTimer = setTimeout(() => {
      blinkHighlight.value = false;
    }, 400);
  }

  function resolveChallengeType() {
    if (typeof challengeTypeFn === "function") return challengeTypeFn();
    return challengeTypeFn?.value ?? "";
  }

  function challengeNeeds(type, action) {
    if (type === "enrollment_sequence") {
      if (action === "blink") return true;
      if (action === "turn_left") return true;
      if (action === "turn_right") return true;
      return false;
    }
    if (action === "blink") return type.includes("blink");
    if (action === "turn_left") return type.includes("turn_left");
    if (action === "turn_right") return type.includes("turn_right");
    return false;
  }

  function getRequiredForType(type) {
    const steps = ["face"];
    if (type === "enrollment_sequence") {
      steps.push("blink", "turn_left", "turn_right");
      return steps;
    }
    if (challengeNeeds(type, "blink")) steps.push("blink");
    if (type === "blink_twice") steps.push("blink2");
    if (challengeNeeds(type, "turn_left")) steps.push("turn_left");
    if (challengeNeeds(type, "turn_right")) steps.push("turn_right");
    return steps;
  }

  function nextActionHint(type) {
    const steps = completedSteps.value;
    if (warning.value) return warning.value;
    if (challengeNeeds(type, "blink") && !steps.has("blink")) return "Blink now";
    if (type === "blink_twice" && steps.has("blink") && !steps.has("blink2")) return "Blink again";
    if (challengeNeeds(type, "turn_left") && !steps.has("turn_left")) return "Turn head left";
    if (challengeNeeds(type, "turn_right") && !steps.has("turn_right")) return "Turn head right";
    if (getRequiredForType(type).every((s) => steps.has(s))) return "Challenge complete — capture frame";
    if (!steps.has("face")) return "Look at the camera";
    return "Hold steady";
  }

  function trackBlink(pts, type, now) {
    if (!challengeNeeds(type, "blink") && type !== "enrollment_sequence") return;

    const offsetY = faceCenterOffset(pts).offsetY;
    const result = blinkDetector.update(pts, { yaw: headYaw(pts), offsetY }, now);

    blinkMetrics.value = {
      leftEar: result.left,
      rightEar: result.right,
      blinkCount: result.count,
      faceConfidence: blinkMetrics.value.faceConfidence,
      challenge: type,
      phase: result.phase,
    };

    if (import.meta.env.DEV) {
      bioDebug.log("ear_frame", {
        left: result.left.toFixed(2),
        right: result.right.toFixed(2),
        threshold: BLINK_EAR_CLOSED_THRESHOLD,
        open: BLINK_EAR_OPEN_THRESHOLD,
        phase: result.phase,
      });
    }

    if (result.blinked) {
      triggerBlinkHighlight();
      bioDebug.log("blink_detected", {
        count: result.count,
        leftEar: result.left.toFixed(2),
        rightEar: result.right.toFixed(2),
      });
      markStep(result.count >= 2 ? "blink2" : "blink");
    }
  }

  function trackHeadTurn(yaw, type) {
    if (challengeNeeds(type, "turn_left") && yaw >= YAW_LEFT_MARK) {
      bioDebug.log("turn_left_detected", { yaw: yaw.toFixed(2) });
      markStep("turn_left");
    }
    if (challengeNeeds(type, "turn_right") && yaw <= YAW_RIGHT_MARK) {
      bioDebug.log("turn_right_detected", { yaw: yaw.toFixed(2) });
      markStep("turn_right");
    }
  }

  function detectGapFor(type) {
    if (!challengeNeeds(type, "blink")) return DETECT_GAP_MS;
    if (type === "blink_twice" && completedSteps.value.has("blink2")) return DETECT_GAP_MS;
    if (completedSteps.value.has("blink") && type !== "blink_twice") return DETECT_GAP_MS;
    return DETECT_GAP_BLINK_MS;
  }

  function analyzeFrame(video, challengeType, checkLighting) {
    const result = detectFaceSnapshot(video);
    if (!result) return;

    const type = challengeType || "";
    const count = result.faceLandmarks?.length || 0;
    const turnActive =
      challengeNeeds(type, "turn_left") || challengeNeeds(type, "turn_right");
    const now = performance.now();

    if (count === 0) {
      landmarks.value = null;
      faceAligned.value = false;
      blinkMetrics.value = {
        ...blinkMetrics.value,
        leftEar: null,
        rightEar: null,
        faceConfidence: 0,
        challenge: type,
      };
      if (hadFace) bioDebug.log("face_lost");
      hadFace = false;
      setWarning("");
      setHint("No face in frame");
      return;
    }

    if (count > 1) {
      setWarning("Multiple faces — only one person");
      bioDebug.warn("multiple_faces");
    } else {
      setWarning("");
    }

    const pts = result.faceLandmarks[0];
    landmarks.value = pts;
    const confidence = estimateFaceConfidence(pts);

    blinkMetrics.value = {
      ...blinkMetrics.value,
      faceConfidence: confidence,
      challenge: type,
    };

    if (!hadFace) {
      bioDebug.log("face_detected");
      hadFace = true;
    }

    markStep("face");

    const yaw = headYaw(pts);
    trackBlink(pts, type, now);
    trackHeadTurn(yaw, type);

    if (checkLighting) {
      cachedLighting = estimateLighting(video);
      lastLightingAt = performance.now();
    }

    if (cachedLighting.level === "low") {
      setWarning("Poor lighting");
      faceAligned.value = false;
    } else if (!isFaceLargeEnough(pts)) {
      setWarning("");
      faceAligned.value = false;
      setHint("Move closer");
    } else if (!isFaceInsideGuide(pts, { relaxed: turnActive })) {
      setWarning("Face outside frame");
      faceAligned.value = false;
    } else {
      if (!warning.value.includes("Multiple")) setWarning("");
      faceAligned.value = true;
    }

    const required = getRequiredForType(type);
    if (required.every((s) => completedSteps.value.has(s))) {
      markStep("ready");
      bioDebug.log("challenge_completed", { type });
    }

    setHint(nextActionHint(type));
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

    if (completedSteps.value.has("ready")) {
      scheduleNextTick(DETECT_IDLE_GAP_MS);
      onFrameCallback?.();
      return;
    }

    inFlight = true;
    const started = performance.now();
    const type = resolveChallengeType();
    const gap = detectGapFor(type);

    requestAnimationFrame(() => {
      try {
        const now = performance.now();
        const checkLighting = now - lastLightingAt >= LIGHTING_INTERVAL_MS;
        analyzeFrame(video, type, checkLighting);
        onFrameCallback?.();
      } finally {
        inFlight = false;
        if (!loopStopped && !loopPaused) {
          const elapsed = performance.now() - started;
          const nextGap = detectGapFor(resolveChallengeType());
          scheduleNextTick(Math.max(nextGap, elapsed + 16));
        }
      }
    });
  }

  function startLoop(videoRef, challengeTypeRef, { onFrame } = {}) {
    stopLoop();
    videoRefForLoop = videoRef;
    challengeTypeFn = challengeTypeRef;
    onFrameCallback = onFrame;
    loopPaused = false;
    loopStopped = false;
    scheduleNextTick(0);
  }

  function stopLoop() {
    loopStopped = true;
    clearDetectTimer();
    inFlight = false;
    onFrameCallback = null;
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
    if (blinkHighlightTimer) clearTimeout(blinkHighlightTimer);
  });

  return {
    loadingPhase,
    engineReady,
    cameraReady,
    landmarks,
    liveHint,
    warning,
    completedSteps,
    blinkHighlight,
    faceAligned,
    blinkMetrics,
    initEngine,
    startLoop,
    stopLoop,
    pauseLoop,
    resumeLoop,
    resetChallengeTracking,
  };
}
