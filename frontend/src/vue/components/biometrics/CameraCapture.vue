<script setup>
import { ref, watch } from "vue";
import { useCamera } from "@/composables/useCamera";
import { VAlert, VButton } from "@/components/ui";

const props = defineProps({
  autoStart: { type: Boolean, default: true },
  compact: { type: Boolean, default: false },
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
  <div :class="compact ? 'flex flex-col items-center gap-2' : 'space-y-4'">
    <VAlert v-if="error" variant="error" :class="compact ? 'w-full' : ''">{{ error }}</VAlert>
    <div
      class="relative overflow-hidden rounded-input border border-border bg-slate-900"
      :class="
        compact
          ? 'vb-camera-preview--compact'
          : 'aspect-[4/3] rounded-card'
      "
    >
      <video
        ref="videoRef"
        class="h-full w-full object-cover mirror"
        playsinline
        muted
        aria-label="Camera preview"
      />
      <div
        v-if="!isActive && !error"
        class="absolute inset-0 flex items-center justify-center bg-slate-800 text-xs text-slate-300 sm:text-sm"
      >
        Starting camera…
      </div>
    </div>
    <div
      :class="
        compact
          ? 'flex w-full max-w-[11rem] items-center gap-2 sm:max-w-[12rem]'
          : 'flex gap-4'
      "
    >
      <VButton
        type="button"
        :variant="compact ? 'secondary' : 'primary'"
        :size="compact ? 'sm' : 'md'"
        block
        @click="handleCapture"
      >
        Capture frame
      </VButton>
      <VButton
        v-if="!isActive"
        type="button"
        variant="ghost"
        :size="compact ? 'sm' : 'md'"
        :class="compact ? 'shrink-0 px-2' : ''"
        @click="start"
      >
        Retry
      </VButton>
    </div>
  </div>
</template>

<style scoped>
.mirror {
  transform: scaleX(-1);
}

.vb-camera-preview--compact {
  aspect-ratio: 1 / 1;
  width: 100%;
  max-width: 11rem;
}

@media (min-width: 640px) {
  .vb-camera-preview--compact {
    max-width: 12rem;
  }
}
</style>
