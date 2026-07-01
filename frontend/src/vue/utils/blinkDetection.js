/**
 * Blink detection via Eye Aspect Ratio (EAR) on MediaPipe Face Landmarker landmarks.
 *
 * Left eye:  [33, 160, 158, 133, 153, 144]
 * Right eye: [362, 385, 387, 263, 373, 380]
 * EAR = (||p2-p6|| + ||p3-p5||) / (2 * ||p1-p4||)
 */

/** Stricter thresholds — require full closure and full reopen. */
export const BLINK_EAR_CLOSED_THRESHOLD = 0.18;
export const BLINK_EAR_OPEN_THRESHOLD = 0.28;

/** Reject one-eye squints and partial lid movement. */
export const BLINK_MAX_EYE_ASYMMETRY = 0.06;

/** Eyes must be open briefly before a blink counts. */
export const BLINK_MIN_OPEN_BEFORE_MS = 120;

/** Normal human blink window (~80–350ms). */
export const BLINK_MIN_CLOSED_MS = 80;
export const BLINK_MAX_CLOSED_MS = 350;

/** Reject head movement and looking down during closure. */
export const BLINK_MAX_HEAD_YAW_DELTA = 0.12;
export const BLINK_MAX_OFFSET_Y_DELTA = 0.06;

const LEFT_EYE = [33, 160, 158, 133, 153, 144];
const RIGHT_EYE = [362, 385, 387, 263, 373, 380];

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

function bothEyesClosed(left, right) {
  return left < BLINK_EAR_CLOSED_THRESHOLD && right < BLINK_EAR_CLOSED_THRESHOLD;
}

function bothEyesOpen(left, right) {
  return left >= BLINK_EAR_OPEN_THRESHOLD && right >= BLINK_EAR_OPEN_THRESHOLD;
}

function eyesSymmetric(left, right) {
  return Math.abs(left - right) <= BLINK_MAX_EYE_ASYMMETRY;
}

/**
 * Stateful blink detector with hysteresis, duration window, and stability guards.
 * No cooldown between valid blinks.
 */
export function createBlinkDetector() {
  let phase = "open";
  let closedAt = 0;
  let openSince = 0;
  let anchorYaw = 0;
  let anchorOffsetY = 0;
  let count = 0;

  function reset() {
    phase = "open";
    closedAt = 0;
    openSince = 0;
    anchorYaw = 0;
    anchorOffsetY = 0;
    count = 0;
  }

  function abortClose(now) {
    phase = "open";
    closedAt = 0;
    openSince = now;
  }

  function update(landmarks, context = {}, now = performance.now()) {
    const { left, right, min } = computeEarSnapshot(landmarks);
    const yaw = context.yaw ?? 0;
    const offsetY = context.offsetY ?? 0;
    let blinked = false;
    let rejected = null;

    if (phase === "open") {
      if (bothEyesOpen(left, right)) {
        openSince = openSince || now;
      } else if (!bothEyesClosed(left, right)) {
        openSince = 0;
      }

      const openDuration = openSince ? now - openSince : 0;
      if (
        bothEyesClosed(left, right) &&
        eyesSymmetric(left, right) &&
        openDuration >= BLINK_MIN_OPEN_BEFORE_MS
      ) {
        phase = "closed";
        closedAt = now;
        anchorYaw = yaw;
        anchorOffsetY = offsetY;
      }
    } else if (phase === "closed") {
      const yawDelta = Math.abs(yaw - anchorYaw);
      const offsetDelta = Math.abs(offsetY - anchorOffsetY);

      if (yawDelta > BLINK_MAX_HEAD_YAW_DELTA) {
        rejected = "head_movement";
        abortClose(now);
      } else if (offsetDelta > BLINK_MAX_OFFSET_Y_DELTA) {
        rejected = "looking_down";
        abortClose(now);
      } else if (!eyesSymmetric(left, right) && !bothEyesClosed(left, right)) {
        rejected = "partial_eyelid";
        abortClose(now);
      } else if (bothEyesOpen(left, right)) {
        const duration = now - closedAt;
        if (
          duration >= BLINK_MIN_CLOSED_MS &&
          duration <= BLINK_MAX_CLOSED_MS &&
          eyesSymmetric(left, right)
        ) {
          count += 1;
          blinked = true;
        }
        phase = "open";
        closedAt = 0;
        openSince = now;
      } else if (now - closedAt > BLINK_MAX_CLOSED_MS) {
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
    };
  }

  return { update, reset, get count() { return count; } };
}
