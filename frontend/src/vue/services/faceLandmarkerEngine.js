/**
 * Shared MediaPipe Face Landmarker — singleton, IMAGE mode on downscaled canvas.
 */

import { bioDebug } from "@/utils/biometricDebug";
import { normalizeLandmarkSet } from "@/utils/faceDetectionUtils";

const WASM_CDN = "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.21/wasm";
const MODEL_URL =
  "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task";

const MEDIAPIPE_CONSOLE_PATTERN =
  /inference_feedback_manager|FaceBlendshapesGraph|gl_context|face_landmarker_graph|TensorFlow Lite XNNPACK|Graph successfully started/;

let mediaPipeConsoleSilenced = false;

function silenceMediaPipeConsoleNoise() {
  if (mediaPipeConsoleSilenced || typeof console === "undefined") return;
  mediaPipeConsoleSilenced = true;

  const originalWarn = console.warn.bind(console);
  const originalLog = console.log.bind(console);

  const shouldSilence = (args) => MEDIAPIPE_CONSOLE_PATTERN.test(String(args[0] ?? ""));

  console.warn = (...args) => {
    if (shouldSilence(args)) return;
    originalWarn(...args);
  };

  console.log = (...args) => {
    if (shouldSilence(args)) return;
    originalLog(...args);
  };
}

export const ANALYSIS_SIZE = 320;

let landmarker = null;
let initPromise = null;
let analysisCanvas = null;
let analysisCtx = null;

function getAnalysisSurface() {
  if (!analysisCanvas) {
    analysisCanvas = document.createElement("canvas");
    analysisCtx = analysisCanvas.getContext("2d", { alpha: false });
  }
  if (analysisCanvas.width !== ANALYSIS_SIZE || analysisCanvas.height !== ANALYSIS_SIZE) {
    analysisCanvas.width = ANALYSIS_SIZE;
    analysisCanvas.height = ANALYSIS_SIZE;
  }
  return { canvas: analysisCanvas, ctx: analysisCtx };
}

export async function getFaceLandmarker() {
  if (landmarker) return landmarker;
  if (initPromise) return initPromise;

  initPromise = (async () => {
    silenceMediaPipeConsoleNoise();
    bioDebug.log("engine_loading");
    const { FaceLandmarker, FilesetResolver } = await import("@mediapipe/tasks-vision");
    const vision = await FilesetResolver.forVisionTasks(WASM_CDN);
    const options = {
      baseOptions: { modelAssetPath: MODEL_URL, delegate: "CPU" },
      runningMode: "IMAGE",
      numFaces: 2,
      outputFaceBlendshapes: false,
      outputFacialTransformationMatrixes: false,
    };
    landmarker = await FaceLandmarker.createFromOptions(vision, options);
    bioDebug.log("engine_ready");
    return landmarker;
  })();

  try {
    return await initPromise;
  } catch (err) {
    initPromise = null;
    bioDebug.error("engine_failed", { message: err?.message });
    throw err;
  }
}

export function detectFaceSnapshot(video) {
  if (!landmarker || !video || video.readyState < 2) return null;

  const { canvas, ctx } = getAnalysisSurface();
  ctx.save();
  ctx.scale(-1, 1);
  ctx.drawImage(video, -ANALYSIS_SIZE, 0, ANALYSIS_SIZE, ANALYSIS_SIZE);
  ctx.restore();
  const result = landmarker.detect(canvas);
  if (!result?.faceLandmarks?.length) return result;
  result.faceLandmarks = result.faceLandmarks.map((set) => normalizeLandmarkSet(set)).filter(Boolean);
  return result;
}

export function releaseFaceLandmarker() {
  landmarker?.close?.();
  landmarker = null;
  initPromise = null;
}
