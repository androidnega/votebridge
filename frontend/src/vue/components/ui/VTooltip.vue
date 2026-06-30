<script setup>
import { ref } from "vue";

const props = defineProps({
  label: {
    type: String,
    required: true,
  },
  position: {
    type: String,
    default: "right",
    validator: (v) => ["right", "top", "bottom"].includes(v),
  },
  disabled: {
    type: Boolean,
    default: false,
  },
});

const triggerRef = ref(null);
const visible = ref(false);
const tooltipStyle = ref({});

function updatePosition() {
  const el = triggerRef.value;
  if (!el) return;

  const rect = el.getBoundingClientRect();
  const gap = 8;

  if (props.position === "right") {
    tooltipStyle.value = {
      top: `${rect.top + rect.height / 2}px`,
      left: `${rect.right + gap}px`,
      transform: "translateY(-50%)",
    };
    return;
  }

  if (props.position === "top") {
    tooltipStyle.value = {
      top: `${rect.top - gap}px`,
      left: `${rect.left + rect.width / 2}px`,
      transform: "translate(-50%, -100%)",
    };
    return;
  }

  tooltipStyle.value = {
    top: `${rect.bottom + gap}px`,
    left: `${rect.left + rect.width / 2}px`,
    transform: "translateX(-50%)",
  };
}

function show() {
  if (props.disabled) return;
  updatePosition();
  visible.value = true;
}

function hide() {
  visible.value = false;
}
</script>

<template>
  <div
    ref="triggerRef"
    class="inline-flex"
    @mouseenter="show"
    @mouseleave="hide"
    @focusin="show"
    @focusout="hide"
  >
    <slot />
  </div>

  <Teleport to="body">
    <span
      v-if="visible"
      role="tooltip"
      class="pointer-events-none fixed z-[200] whitespace-nowrap rounded-input bg-slate-900 px-2.5 py-1.5 text-xs font-medium text-white shadow-card"
      :style="tooltipStyle"
    >
      {{ label }}
    </span>
  </Teleport>
</template>
