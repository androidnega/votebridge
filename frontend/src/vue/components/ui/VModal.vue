<script setup>
import { onMounted, onUnmounted, watch } from "vue";
import VButton from "./VButton.vue";

const props = defineProps({
  modelValue: Boolean,
  title: String,
  size: {
    type: String,
    default: "md",
  },
  closeOnBackdrop: {
    type: Boolean,
    default: true,
  },
});

const emit = defineEmits(["update:modelValue", "close"]);

const sizeClasses = {
  sm: "max-w-md",
  md: "max-w-lg",
  lg: "max-w-2xl",
  xl: "max-w-4xl",
};

function close() {
  emit("update:modelValue", false);
  emit("close");
}

function onKeydown(event) {
  if (event.key === "Escape" && props.modelValue) {
    close();
  }
}

watch(
  () => props.modelValue,
  (open) => {
    document.body.style.overflow = open ? "hidden" : "";
  }
);

onMounted(() => window.addEventListener("keydown", onKeydown));
onUnmounted(() => {
  window.removeEventListener("keydown", onKeydown);
  document.body.style.overflow = "";
});
</script>

<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="modelValue"
        class="fixed inset-0 z-50 flex items-end justify-center p-4 sm:items-center"
        @click.self="closeOnBackdrop && close()"
      >
        <div class="fixed inset-0 bg-slate-900/50" aria-hidden="true" />
        <div
          class="relative w-full rounded-xl bg-white shadow-xl"
          :class="sizeClasses[size]"
          role="dialog"
          aria-modal="true"
          :aria-labelledby="title ? 'vb-modal-title' : undefined"
        >
          <div class="flex items-start justify-between border-b border-slate-100 px-6 py-4">
            <h2 v-if="title" id="vb-modal-title" class="text-lg font-semibold text-slate-900">{{ title }}</h2>
            <VButton
              variant="ghost"
              size="sm"
              class="min-h-touch !p-2"
              aria-label="Close dialog"
              @click="close"
            >
              ✕
            </VButton>
          </div>
          <div class="px-6 py-4">
            <slot />
          </div>
          <div v-if="$slots.footer" class="border-t border-slate-100 px-6 py-4">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
