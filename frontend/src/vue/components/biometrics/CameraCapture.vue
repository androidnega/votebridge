<script setup>
import { ref, watch } from "vue";
import { useCamera } from "@/composables/useCamera";
import { VAlert, VButton } from "@/components/ui";

const props = defineProps({
  autoStart: { type: Boolean, default: true },
});

const emit = defineEmits(["frame", "error"]);

const { videoRef, error, isActive, start, stop, captureFrame } = useCamera();

watch(error, (val) => {
  if (val) emit("error", val);
});

function handleCapture() {
  const frame = captureFrame();
  if (frame) emit("frame", frame);
}

defineExpose({ captureFrame, start, stop });
</script>

<template>
  <div class="space-y-4">
    <VAlert v-if="error" variant="error">{{ error }}</VAlert>
    <div class="relative overflow-hidden rounded-card border border-border bg-slate-900 aspect-[4/3]">
      <video
        ref="videoRef"
        class="h-full w-full object-cover mirror"
        playsinline
        muted
        aria-label="Camera preview"
      />
      <div
        v-if="!isActive && !error"
        class="absolute inset-0 flex items-center justify-center bg-slate-800 text-slate-300 text-sm"
      >
        Starting camera…
      </div>
    </div>
    <div class="flex gap-4">
      <VButton type="button" variant="primary" block @click="handleCapture">
        Capture frame
      </VButton>
      <VButton v-if="!isActive" type="button" variant="secondary" @click="start">
        Retry camera
      </VButton>
    </div>
  </div>
</template>

<style scoped>
.mirror {
  transform: scaleX(-1);
}
</style>
