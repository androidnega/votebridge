/**
 * Blink detection via Eye Aspect Ratio (EAR) on MediaPipe Face Landmarker landmarks.
 *
 * Left eye:  [33, 160, 158, 133, 153, 144]
 * Right eye: [362, 385, 387, 263, 373, 380]
 * EAR = (||p2-p6|| + ||p3-p5||) / (2 * ||p1-p4||)
 */

/** Default thresholds (enrollment / strict). */
export const BLINK_EAR_CLOSED_THRESHOLD = 0.18;
export const BLINK_EAR_OPEN_THRESHOLD = 0.26;

/** Reject one-eye squints and partial lid movement. */
export const BLINK_MAX_EYE_ASYMMETRY = 0.06;

/** Eyes must be open steadily before a blink can register. */
export const BLINK_MIN_OPEN_BEFORE_MS = 150;

/** Normal human blink window (~80–350ms). */
export const BLINK_MIN_CLOSED_MS = 80;
export const BLINK_MAX_CLOSED_MS = 400;

/** Minimum gap between counted blinks (prevents double-count from noise). */
export const BLINK_MIN_GAP_MS = 500;

/** Reject head movement and looking down during closure. */
export const BLINK_MAX_HEAD_YAW_DELTA = 0.12;
export const BLINK_MAX_OFFSET_Y_DELTA = 0.06;

const LEFT_EYE = [33, 160, 158, 133, 153, 144];
const RIGHT_EYE = [362, 385, 387, 263, 373, 380];

const BLINK_PROFILES = {
  verify: {
    adaptive: true,
    calibrateFrames: 4,
    closeDrop: 0.10,
    closeRatio: 0.75,
    openDrop: 0.04,
    openRatio: 0.9,
    maxAsymmetry: 0.15,
    minOpenBeforeMs: 100,
    minClosedMs: 50,
    maxClosedMs: 500,
    minGapMs: 300,
    maxHeadYawDelta: 0.3,
    maxOffsetYDelta: 0.15,
  },
  enrollment: {
    adaptive: false,
    closedThreshold: BLINK_EAR_CLOSED_THRESHOLD,
    openThreshold: BLINK_EAR_OPEN_THRESHOLD,
    baselineMin: BLINK_EAR_CLOSED_THRESHOLD,
    maxAsymmetry: BLINK_MAX_EYE_ASYMMETRY,
    minOpenBeforeMs: BLINK_MIN_OPEN_BEFORE_MS,
    minClosedMs: BLINK_MIN_CLOSED_MS,
    maxClosedMs: BLINK_MAX_CLOSED_MS,
    minGapMs: BLINK_MIN_GAP_MS,
    maxHeadYawDelta: BLINK_MAX_HEAD_YAW_DELTA,
    maxOffsetYDelta: BLINK_MAX_OFFSET_Y_DELTA,
  },
};

function dist(a, b) {
  return Math.hypot(a.x - b.x, a.y - b.y);
}

export function eyeAspectRatio(landmarks, indices) {
  const p = indices.map((i) => landmarks[i]);
  if (p.some((pt) => !pt)) return 1;
  const vertical = dist(p[1], p[5]) + dist(p[2], p[4]);
  const horizontal = dist(p[0], p[3]);
  if (!horizontal) return 1;
  return vertical / (2 * horizontal);
}

export function leftEyeEar(landmarks) {
  return eyeAspectRatio(landmarks, LEFT_EYE);
}

export function rightEyeEar(landmarks) {
  return eyeAspectRatio(landmarks, RIGHT_EYE);
}

export function averageEar(landmarks) {
  return (leftEyeEar(landmarks) + rightEyeEar(landmarks)) / 2;
}

export function minEar(landmarks) {
  return Math.min(leftEyeEar(landmarks), rightEyeEar(landmarks));
}

export function computeEarSnapshot(landmarks) {
  const left = leftEyeEar(landmarks);
  const right = rightEyeEar(landmarks);
  return {
    left,
    right,
    avg: (left + right) / 2,
    min: Math.min(left, right),
  };
}

export function isEarClosed(ear) {
  return ear < BLINK_EAR_CLOSED_THRESHOLD;
}

export function isEarOpen(ear) {
  return ear >= BLINK_EAR_OPEN_THRESHOLD;
}

function eyesSymmetric(left, right, maxAsymmetry) {
  return Math.abs(left - right) <= maxAsymmetry;
}

function computeAdaptiveThresholds(baseline, config) {
  const closeAt = Math.min(baseline - config.closeDrop, baseline * config.closeRatio);
  const openAt = Math.max(baseline - config.openDrop, baseline * config.openRatio);
  return { baseline, closeAt, openAt };
}

function isAdaptiveClosed(min, thresholds) {
  return thresholds.baseline > 0 && min < thresholds.closeAt;
}

function isAdaptiveOpen(min, thresholds) {
  return thresholds.baseline > 0 && min >= thresholds.openAt;
}

/**
 * Stateful blink detector with hysteresis, duration window, and stability guards.
 * Verify profile uses adaptive thresholds from the user's resting EAR (~0.35–0.45).
 */
export function createBlinkDetector({ profile = "enrollment" } = {}) {
  const config = BLINK_PROFILES[profile] || BLINK_PROFILES.enrollment;

  let phase = "open";
  let closedAt = 0;
  let openSince = 0;
  let anchorYaw = 0;
  let anchorOffsetY = 0;
  let count = 0;
  let lastBlinkAt = 0;
  let baselineEar = 0;
  let calibrateCount = 0;
  let thresholds = { baseline: 0, closeAt: 0, openAt: 0 };

  function reset() {
    phase = "open";
    closedAt = 0;
    openSince = 0;
    anchorYaw = 0;
    anchorOffsetY = 0;
    count = 0;
    lastBlinkAt = 0;
    baselineEar = 0;
    calibrateCount = 0;
    thresholds = { baseline: 0, closeAt: 0, openAt: 0 };
  }

  function abortClose(now) {
    phase = "open";
    closedAt = 0;
    openSince = now;
  }

  function updateAdaptive(left, right, min, yaw, offsetY, now) {
    let blinked = false;
    let rejected = null;

    if (phase === "open" && !isAdaptiveClosed(min, thresholds)) {
      baselineEar = Math.max(baselineEar, min);
      calibrateCount += 1;
      if (calibrateCount >= config.calibrateFrames) {
        thresholds = computeAdaptiveThresholds(baselineEar, config);
      }
      openSince = openSince || now;
    }

    if (calibrateCount < config.calibrateFrames) {
      return {
        left,
        right,
        min,
        count,
        blinked,
        phase: "calibrating",
        rejected,
        closedMs: 0,
        baseline: baselineEar,
        closeAt: thresholds.closeAt,
        openAt: thresholds.openAt,
      };
    }

    if (phase === "open") {
      const openDuration = openSince ? now - openSince : 0;
      if (
        isAdaptiveClosed(min, thresholds) &&
        eyesSymmetric(left, right, config.maxAsymmetry) &&
        openDuration >= config.minOpenBeforeMs
      ) {
        phase = "closed";
        closedAt = now;
        anchorYaw = yaw;
        anchorOffsetY = offsetY;
      }
    } else if (phase === "closed") {
      const yawDelta = Math.abs(yaw - anchorYaw);
      const offsetDelta = Math.abs(offsetY - anchorOffsetY);

      if (yawDelta > config.maxHeadYawDelta) {
        rejected = "head_movement";
        abortClose(now);
      } else if (offsetDelta > config.maxOffsetYDelta) {
        rejected = "looking_down";
        abortClose(now);
      } else if (!eyesSymmetric(left, right, config.maxAsymmetry) && !isAdaptiveClosed(min, thresholds)) {
        rejected = "partial_eyelid";
        abortClose(now);
      } else if (isAdaptiveOpen(min, thresholds)) {
        const duration = now - closedAt;
        if (
          duration >= config.minClosedMs &&
          duration <= config.maxClosedMs &&
          eyesSymmetric(left, right, config.maxAsymmetry) &&
          now - lastBlinkAt >= config.minGapMs
        ) {
          count += 1;
          blinked = true;
          lastBlinkAt = now;
        }
        phase = "open";
        closedAt = 0;
        openSince = now;
        baselineEar = Math.max(baselineEar, min);
        thresholds = computeAdaptiveThresholds(baselineEar, config);
      } else if (now - closedAt > config.maxClosedMs) {
        rejected = "squint_held";
        abortClose(now);
      }
    }

    return {
      left,
      right,
      min,
      count,
      blinked,
      phase,
      rejected,
      closedMs: phase === "closed" && closedAt ? now - closedAt : 0,
      baseline: thresholds.baseline,
      closeAt: thresholds.closeAt,
      openAt: thresholds.openAt,
    };
  }

  function updateFixed(left, right, min, yaw, offsetY, now) {
    let blinked = false;
    let rejected = null;

    if (phase === "open") {
      if (min >= config.baselineMin) {
        openSince = openSince || now;
      }

      const openDuration = openSince ? now - openSince : 0;
      if (
        min < config.closedThreshold &&
        eyesSymmetric(left, right, config.maxAsymmetry) &&
        openDuration >= config.minOpenBeforeMs
      ) {
        phase = "closed";
        closedAt = now;
        anchorYaw = yaw;
        anchorOffsetY = offsetY;
      }
    } else if (phase === "closed") {
      const yawDelta = Math.abs(yaw - anchorYaw);
      const offsetDelta = Math.abs(offsetY - anchorOffsetY);

      if (yawDelta > config.maxHeadYawDelta) {
        rejected = "head_movement";
        abortClose(now);
      } else if (offsetDelta > config.maxOffsetYDelta) {
        rejected = "looking_down";
        abortClose(now);
      } else if (!eyesSymmetric(left, right, config.maxAsymmetry) && min >= config.closedThreshold) {
        rejected = "partial_eyelid";
        abortClose(now);
      } else if (min >= config.openThreshold) {
        const duration = now - closedAt;
        if (
          duration >= config.minClosedMs &&
          duration <= config.maxClosedMs &&
          eyesSymmetric(left, right, config.maxAsymmetry) &&
          now - lastBlinkAt >= config.minGapMs
        ) {
          count += 1;
          blinked = true;
          lastBlinkAt = now;
        }
        phase = "open";
        closedAt = 0;
        openSince = now;
      } else if (now - closedAt > config.maxClosedMs) {
        rejected = "squint_held";
        abortClose(now);
      }
    }

    return {
      left,
      right,
      min,
      count,
      blinked,
      phase,
      rejected,
      closedMs: phase === "closed" && closedAt ? now - closedAt : 0,
      baseline: 0,
      closeAt: config.closedThreshold,
      openAt: config.openThreshold,
    };
  }

  function update(landmarks, context = {}, now = performance.now()) {
    const { left, right, min } = computeEarSnapshot(landmarks);
    const yaw = context.yaw ?? 0;
    const offsetY = context.offsetY ?? 0;

    if (config.adaptive) {
      return updateAdaptive(left, right, min, yaw, offsetY, now);
    }
    return updateFixed(left, right, min, yaw, offsetY, now);
  }

  return { update, reset, get count() { return count; } };
}
