import { computed, onMounted, onUnmounted, ref } from "vue";
import { useCamera } from "@/composables/useCamera";
import { detectFaceSnapshot, getFaceLandmarker } from "@/services/faceLandmarkerEngine";
import {
  isFaceLargeEnough,
  isValidLandmarkSet,
  VERIFY_MIN_FACE_WIDTH,
} from "@/utils/faceDetectionUtils";
import { createSignalStabilizer } from "@/utils/signalStabilizer";

const DETECTION_INTERVAL_MS = 180;

export function useFacePresence() {
  const { videoRef, error: cameraError, isActive, start, stop, captureFrame } = useCamera({
    autoStart: false,
    highQuality: true,
  });

  const engineReady = ref(false);
  const engineError = ref("");
  const faceDetected = ref(false);
  const statusKey = ref("initializing");

  const facePresence = createSignalStabilizer({ enterCount: 2, exitCount: 4 });
  let detectionTimer = null;

  const statusText = computed(() => {
    const map = {
      initializing: "Starting camera…",
      camera_error: cameraError.value || "Camera unavailable",
      engine_error: engineError.value || "Face detection unavailable",
      camera_ready: "Camera ready",
      no_face: "No face detected",
      face_detected: "Face detected — you can take your photo",
    };
    return map[statusKey.value] || map.camera_ready;
  });

  function updateStatus() {
    if (cameraError.value) {
      statusKey.value = "camera_error";
      return;
    }
    if (engineError.value) {
      statusKey.value = "engine_error";
      return;
    }
    if (!isActive.value || !engineReady.value) {
      statusKey.value = isActive.value ? "camera_ready" : "initializing";
      return;
    }
    statusKey.value = faceDetected.value ? "face_detected" : "no_face";
  }

  function analyzeFrame() {
    if (!engineReady.value || !videoRef.value) return;
    const result = detectFaceSnapshot(videoRef.value);
    const landmarks = result?.faceLandmarks?.[0];
    const hasFace =
      isValidLandmarkSet(landmarks) &&
      isFaceLargeEnough(landmarks, { minWidth: VERIFY_MIN_FACE_WIDTH });
    faceDetected.value = facePresence.update(hasFace);
    updateStatus();
  }

  function startDetectionLoop() {
    stopDetectionLoop();
    detectionTimer = window.setInterval(analyzeFrame, DETECTION_INTERVAL_MS);
  }

  function stopDetectionLoop() {
    if (detectionTimer) {
      window.clearInterval(detectionTimer);
      detectionTimer = null;
    }
  }

  async function initialize() {
    engineError.value = "";
    try {
      await getFaceLandmarker();
      engineReady.value = true;
      await start();
      startDetectionLoop();
      updateStatus();
    } catch (err) {
      engineError.value = err?.message || "Unable to start face detection.";
      engineReady.value = false;
      updateStatus();
    }
  }

  function takePhoto() {
    return captureFrame();
  }

  onMounted(() => {
    initialize();
  });

  onUnmounted(() => {
    stopDetectionLoop();
    stop();
    facePresence.reset();
  });

  return {
    videoRef,
    cameraError,
    engineError,
    isActive,
    engineReady,
    faceDetected,
    statusText,
    statusKey,
    takePhoto,
    initialize,
    stop,
  };
}
