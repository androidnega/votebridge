import { computed, onMounted, onUnmounted, ref } from "vue";
import { useCamera } from "@/composables/useCamera";

/**
 * Pre-vote presence capture — camera only (no ML face detection).
 * Photo capture is enabled once the camera stream is active.
 */
export function useFacePresence() {
  const { videoRef, error: cameraError, isActive, start, stop, captureFrame } = useCamera({
    autoStart: false,
    highQuality: true,
  });

  const statusKey = ref("initializing");
  const engineError = ref("");

  const faceDetected = computed(() => isActive.value && !cameraError.value);

  const statusText = computed(() => {
    const map = {
      initializing: "Starting camera…",
      camera_error: cameraError.value || "Camera unavailable",
      camera_ready: "Position your face in the frame",
      ready: "Camera ready — tap Take Photo",
    };
    return map[statusKey.value] || map.camera_ready;
  });

  function updateStatus() {
    if (cameraError.value) {
      statusKey.value = "camera_error";
      return;
    }
    statusKey.value = isActive.value ? "ready" : "initializing";
  }

  async function initialize() {
    await start();
    updateStatus();
  }

  function takePhoto() {
    return captureFrame();
  }

  onMounted(() => {
    initialize();
  });

  onUnmounted(() => {
    stop();
  });

  return {
    videoRef,
    cameraError,
    engineError,
    isActive,
    engineReady: computed(() => isActive.value),
    faceDetected,
    statusText,
    statusKey,
    takePhoto,
    initialize,
    stop,
  };
}
