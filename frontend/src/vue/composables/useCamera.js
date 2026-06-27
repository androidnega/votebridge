import { onMounted, onUnmounted, ref } from "vue";

export function useCamera() {
  const videoRef = ref(null);
  const stream = ref(null);
  const error = ref("");
  const isActive = ref(false);

  async function start() {
    error.value = "";
    try {
      const media = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "user", width: { ideal: 640 }, height: { ideal: 480 } },
        audio: false,
      });
      stream.value = media;
      if (videoRef.value) {
        videoRef.value.srcObject = media;
        await videoRef.value.play();
      }
      isActive.value = true;
    } catch (err) {
      error.value = err?.message || "Camera access denied.";
      isActive.value = false;
    }
  }

  function stop() {
    if (stream.value) {
      stream.value.getTracks().forEach((track) => track.stop());
      stream.value = null;
    }
    if (videoRef.value) {
      videoRef.value.srcObject = null;
    }
    isActive.value = false;
  }

  function captureFrame() {
    if (!videoRef.value) return null;
    const canvas = document.createElement("canvas");
    canvas.width = videoRef.value.videoWidth || 640;
    canvas.height = videoRef.value.videoHeight || 480;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(videoRef.value, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL("image/jpeg", 0.85);
  }

  onMounted(() => {
    start();
  });

  onUnmounted(() => {
    stop();
  });

  return { videoRef, stream, error, isActive, start, stop, captureFrame };
}
