import { describe, expect, it } from "vitest";
import {
  ENROLL_MIN_FACE_WIDTH,
  faceBoundingBox,
  isFaceLargeEnough,
  isValidLandmarkSet,
  normalizeLandmarkSet,
  VERIFY_MIN_FACE_WIDTH,
} from "@/utils/faceDetectionUtils";

function mockLandmarks(width = 0.3) {
  return [
    { x: 0.5 - width / 2, y: 0.4 },
    { x: 0.5 + width / 2, y: 0.6 },
  ];
}

describe("faceDetectionUtils", () => {
  it("rejects invalid landmark sets", () => {
    expect(isValidLandmarkSet(null)).toBe(false);
    expect(isValidLandmarkSet(undefined)).toBe(false);
    expect(isValidLandmarkSet({})).toBe(false);
    expect(isValidLandmarkSet([])).toBe(false);
    expect(isValidLandmarkSet(mockLandmarks())).toBe(true);
  });

  it("faceBoundingBox does not throw on invalid input", () => {
    expect(faceBoundingBox(null)).toEqual({
      minX: 0,
      minY: 0,
      maxX: 0,
      maxY: 0,
      width: 0,
      height: 0,
    });
    expect(isFaceLargeEnough(null)).toBe(false);
  });

  it("normalizes array-like landmark sets", () => {
    const arrayLike = {
      length: 2,
      0: { x: 0.4, y: 0.4 },
      1: { x: 0.6, y: 0.6 },
    };
    expect(normalizeLandmarkSet(arrayLike)).toHaveLength(2);
  });

  it("uses relaxed minimum width for verify mode", () => {
    const landmarks = [
      { x: 0.44, y: 0.4 },
      { x: 0.56, y: 0.6 },
    ];
    expect(isFaceLargeEnough(landmarks, { minWidth: VERIFY_MIN_FACE_WIDTH })).toBe(true);
    expect(isFaceLargeEnough(landmarks, { minWidth: ENROLL_MIN_FACE_WIDTH })).toBe(false);
  });
});
