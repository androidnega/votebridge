import { describe, expect, it } from "vitest";
import {
  BLINK_EAR_CLOSED_THRESHOLD,
  BLINK_EAR_OPEN_THRESHOLD,
  BLINK_MAX_CLOSED_MS,
  BLINK_MIN_CLOSED_MS,
  BLINK_MIN_OPEN_BEFORE_MS,
  computeEarSnapshot,
  createBlinkDetector,
  leftEyeEar,
  rightEyeEar,
} from "@/utils/blinkDetection";

function pt(x, y) {
  return { x, y };
}

function makeLandmarks({ leftOpen = true, rightOpen = true } = {}) {
  const landmarks = Array.from({ length: 478 }, () => pt(0.5, 0.5));

  const leftWide = leftOpen ? 0.04 : 0.006;
  const rightWide = rightOpen ? 0.04 : 0.006;

  landmarks[33] = pt(0.35, 0.42);
  landmarks[133] = pt(0.45, 0.42);
  landmarks[160] = pt(0.38, 0.42 - leftWide / 2);
  landmarks[158] = pt(0.40, 0.42 - leftWide / 3);
  landmarks[153] = pt(0.40, 0.42 + leftWide / 3);
  landmarks[144] = pt(0.38, 0.42 + leftWide / 2);

  landmarks[263] = pt(0.65, 0.42);
  landmarks[362] = pt(0.55, 0.42);
  landmarks[385] = pt(0.62, 0.42 - rightWide / 2);
  landmarks[387] = pt(0.60, 0.42 - rightWide / 3);
  landmarks[373] = pt(0.60, 0.42 + rightWide / 3);
  landmarks[380] = pt(0.62, 0.42 + rightWide / 2);

  return landmarks;
}

describe("blinkDetection EAR", () => {
  it("uses MediaPipe six-point eye landmark indices", () => {
    const open = makeLandmarks();
    const closed = makeLandmarks({ leftOpen: false, rightOpen: false });

    const openEar = computeEarSnapshot(open);
    const closedEar = computeEarSnapshot(closed);

    expect(openEar.left).toBeGreaterThan(BLINK_EAR_CLOSED_THRESHOLD);
    expect(openEar.right).toBeGreaterThan(BLINK_EAR_CLOSED_THRESHOLD);
    expect(closedEar.left).toBeLessThan(BLINK_EAR_CLOSED_THRESHOLD);
    expect(closedEar.right).toBeLessThan(BLINK_EAR_CLOSED_THRESHOLD);
  });

  it("computes vertical pairs p2-p6 and p3-p5", () => {
    const landmarks = makeLandmarks();
    expect(leftEyeEar(landmarks)).toBeCloseTo(0.33, 1);
    expect(rightEyeEar(landmarks)).toBeCloseTo(0.33, 1);
  });
});

describe("createBlinkDetector", () => {
  it("detects closed→open transition within duration window", () => {
    const detector = createBlinkDetector();
    const open = makeLandmarks();
    const closed = makeLandmarks({ leftOpen: false, rightOpen: false });
    let t = 1000;

    for (let i = 0; i < 5; i += 1) {
      detector.update(open, { yaw: 0, offsetY: 0 }, t);
      t += 30;
    }
    t += BLINK_MIN_OPEN_BEFORE_MS;

    detector.update(closed, { yaw: 0, offsetY: 0 }, t);
    t += BLINK_MIN_CLOSED_MS;
    const result = detector.update(open, { yaw: 0, offsetY: 0 }, t);
    expect(result.blinked).toBe(true);
    expect(result.count).toBe(1);
  });

  it("rejects eyes held closed too long", () => {
    const detector = createBlinkDetector();
    const open = makeLandmarks();
    const closed = makeLandmarks({ leftOpen: false, rightOpen: false });
    let t = 0;

    for (let i = 0; i < 5; i += 1) {
      detector.update(open, {}, t);
      t += 40;
    }
    t += BLINK_MIN_OPEN_BEFORE_MS;
    detector.update(closed, {}, t);
    t += BLINK_MAX_CLOSED_MS + 50;
    const result = detector.update(open, {}, t);
    expect(result.blinked).toBe(false);
    expect(result.count).toBe(0);
  });

  it("rejects partial one-eye closure", () => {
    const detector = createBlinkDetector();
    const open = makeLandmarks();
    const partial = makeLandmarks({ leftOpen: false, rightOpen: true });
    let t = 0;

    for (let i = 0; i < 5; i += 1) {
      detector.update(open, {}, t);
      t += 40;
    }
    t += BLINK_MIN_OPEN_BEFORE_MS;
    const result = detector.update(partial, {}, t);
    expect(result.phase).toBe("open");
    expect(result.blinked).toBe(false);
  });

  it("rejects head movement during closure", () => {
    const detector = createBlinkDetector();
    const open = makeLandmarks();
    const closed = makeLandmarks({ leftOpen: false, rightOpen: false });
    let t = 0;

    for (let i = 0; i < 5; i += 1) {
      detector.update(open, { yaw: 0, offsetY: 0 }, t);
      t += 40;
    }
    t += BLINK_MIN_OPEN_BEFORE_MS;
    detector.update(closed, { yaw: 0, offsetY: 0 }, t);
    t += 100;
    const result = detector.update(open, { yaw: 0.2, offsetY: 0 }, t);
    expect(result.blinked).toBe(false);
    expect(result.rejected).toBe("head_movement");
  });

  it("uses hysteresis between closed and open thresholds", () => {
    expect(BLINK_EAR_OPEN_THRESHOLD).toBeGreaterThan(BLINK_EAR_CLOSED_THRESHOLD);
  });
});
