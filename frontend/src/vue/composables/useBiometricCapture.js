import { ref } from "vue";

const FRAME_GAP_MS = 400;

function wait(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Sequential frame capture after liveness challenge completes.
 */
export function useBiometricCapture({ framesRequired, onFrame }) {
  const capturing = ref(false);
  const framesCaptured = ref(0);
  let captureLock = false;

  async function captureSequence(captureFrame, { canCapture } = {}) {
    if (captureLock || capturing.value) return;
    if (canCapture && !canCapture()) return;

    captureLock = true;
    capturing.value = true;

    try {
      for (let i = framesCaptured.value; i < framesRequired; i += 1) {
        if (i > 0) await wait(FRAME_GAP_MS);
        const frame = captureFrame?.();
        if (!frame) break;
        framesCaptured.value += 1;
        await onFrame?.(frame);
      }
    } finally {
      capturing.value = false;
      captureLock = false;
    }
  }

  function resetCapture() {
    framesCaptured.value = 0;
    captureLock = false;
    capturing.value = false;
  }

  return {
    capturing,
    framesCaptured,
    captureSequence,
    resetCapture,
  };
}
