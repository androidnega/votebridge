import { faceBoundingBox } from "@/utils/faceDetectionUtils";

/**
 * Minimal scanner overlay — alignment rectangle only (production UX).
 */
export function drawScannerOverlay(ctx, { width, height, landmarks, faceAligned }) {
  ctx.clearRect(0, 0, width, height);

  if (!landmarks?.length) return;

  const box = faceBoundingBox(landmarks);
  const x = box.minX * width;
  const y = box.minY * height;
  const w = box.width * width;
  const h = box.height * height;

  ctx.strokeStyle = faceAligned ? "rgba(22, 163, 74, 0.9)" : "rgba(217, 119, 6, 0.85)";
  ctx.lineWidth = 2;
  ctx.strokeRect(x, y, w, h);
}

export function faceStatusLabel({ hasFace, faceAligned, warning }) {
  if (warning?.includes("Multiple")) return { text: warning, tone: "warning" };
  if (!hasFace) return { text: "Face not detected", tone: "lost" };
  if (!faceAligned) return { text: "Align your face", tone: "warning" };
  return { text: "Face detected", tone: "ok" };
}
