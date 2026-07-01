/** Client-side face analysis helpers for live UX feedback (not used for verification). */

import {
  averageEar,
  isEarClosed,
  leftEyeEar,
  minEar,
  rightEyeEar,
} from "@/utils/blinkDetection";

export {
  averageEar,
  leftEyeEar,
  rightEyeEar,
  minEar,
  BLINK_EAR_CLOSED_THRESHOLD,
  BLINK_EAR_OPEN_THRESHOLD,
} from "@/utils/blinkDetection";

function dist(a, b) {
  return Math.hypot(a.x - b.x, a.y - b.y);
}

/** @deprecated Use EAR via blinkDetection — kept for overlay tint. */
export function isBlinkFrame(landmarks) {
  return isEarClosed(minEar(landmarks));
}

export function isEyeOpen(ear) {
  return ear > 0.16 && ear < 0.42;
}

/** Mouth width vs height — higher values suggest a smile (UX hint only). */
export function smileRatio(landmarks) {
  const top = landmarks[13];
  const bottom = landmarks[14];
  const left = landmarks[61];
  const right = landmarks[291];
  if (!top || !bottom || !left || !right) return 0;
  const height = dist(top, bottom) || 0.001;
  const width = dist(left, right);
  return width / height;
}

export function isSmiling(landmarks) {
  return smileRatio(landmarks) > 3.2;
}

/** Whether the face bbox sits mostly inside the oval guide region. */
export function isFaceInsideGuide(landmarks, { relaxed = false } = {}) {
  const box = faceBoundingBox(landmarks);
  const cx = (box.minX + box.maxX) / 2;
  const cy = (box.minY + box.maxY) / 2;
  const marginX = relaxed ? 0.32 : 0.22;
  const marginY = relaxed ? 0.36 : 0.28;
  const inOvalX = Math.abs(cx - 0.5) < marginX;
  const inOvalY = Math.abs(cy - 0.46) < marginY;
  const edge = relaxed ? 0.02 : 0.05;
  return inOvalX && inOvalY && box.minX > edge && box.maxX < 1 - edge && box.minY > edge && box.maxY < 1 - edge;
}

export function eyeCenterY(landmarks, side) {
  const indices = side === "left" ? [33, 133, 159, 145] : [362, 263, 386, 374];
  const pts = indices.map((i) => landmarks[i]).filter(Boolean);
  if (!pts.length) return 0.45;
  return pts.reduce((sum, p) => sum + p.y, 0) / pts.length;
}

export function faceBoundingBox(landmarks) {
  let minX = 1;
  let minY = 1;
  let maxX = 0;
  let maxY = 0;
  for (const pt of landmarks) {
    minX = Math.min(minX, pt.x);
    minY = Math.min(minY, pt.y);
    maxX = Math.max(maxX, pt.x);
    maxY = Math.max(maxY, pt.y);
  }
  return { minX, minY, maxX, maxY, width: maxX - minX, height: maxY - minY };
}

export function faceCenterOffset(landmarks) {
  const box = faceBoundingBox(landmarks);
  const cx = (box.minX + box.maxX) / 2;
  const cy = (box.minY + box.maxY) / 2;
  return {
    offsetX: cx - 0.5,
    offsetY: cy - 0.5,
    centered: Math.abs(cx - 0.5) < 0.08 && Math.abs(cy - 0.5) < 0.1,
    faceSize: box.width,
  };
}

/** Positive yaw ≈ user turned head to their left (matches backend head_yaw). */
export function headYaw(landmarks) {
  const nose = landmarks[1];
  if (!nose) return 0;
  return (nose.x - 0.5) * 2;
}

export function estimateLighting(video) {
  if (!video || video.readyState < 2) return { level: "unknown", score: 0.5 };
  if (!estimateLighting._canvas) {
    estimateLighting._canvas = document.createElement("canvas");
    estimateLighting._canvas.width = 32;
    estimateLighting._canvas.height = 24;
    estimateLighting._ctx = estimateLighting._canvas.getContext("2d", { willReadFrequently: true });
  }
  const canvas = estimateLighting._canvas;
  const ctx = estimateLighting._ctx;
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  const data = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
  let sum = 0;
  for (let i = 0; i < data.length; i += 16) {
    sum += 0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2];
  }
  const avg = sum / (data.length / 16) / 255;
  if (avg < 0.22) return { level: "low", score: avg };
  if (avg > 0.92) return { level: "high", score: avg };
  return { level: "ok", score: avg };
}

export function isFaceLargeEnough(landmarks) {
  return faceBoundingBox(landmarks).width > 0.22;
}

export const MESH_CONNECTIONS = {
  faceOval: [
    [10, 338], [338, 297], [297, 332], [332, 284], [284, 251], [251, 389], [389, 356],
    [356, 454], [454, 323], [323, 361], [361, 288], [288, 397], [397, 365], [365, 379],
    [379, 378], [378, 400], [400, 377], [377, 152], [152, 148], [148, 176], [176, 149],
    [149, 150], [150, 136], [136, 172], [172, 58], [58, 132], [132, 93], [93, 234],
    [234, 127], [127, 162], [162, 21], [21, 54], [54, 103], [103, 67], [67, 109],
    [109, 10],
  ],
  leftEye: [[33, 7], [7, 163], [163, 144], [144, 145], [145, 153], [153, 154], [154, 155], [155, 133], [133, 173], [173, 157], [157, 158], [158, 159], [159, 160], [160, 161], [161, 246], [246, 33]],
  rightEye: [[362, 382], [382, 381], [381, 380], [380, 374], [374, 373], [373, 390], [390, 249], [249, 263], [263, 466], [466, 388], [388, 387], [387, 386], [386, 385], [385, 384], [384, 398], [398, 362]],
  lips: [[61, 146], [146, 91], [91, 181], [181, 84], [84, 17], [17, 314], [314, 405], [405, 321], [321, 375], [375, 291], [291, 61]],
  nose: [[168, 6], [6, 197], [197, 195], [195, 5], [5, 4], [4, 1], [1, 19], [19, 94], [94, 2]],
};
