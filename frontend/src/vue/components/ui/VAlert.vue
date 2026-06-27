<script setup>
import { computed } from "vue";

const props = defineProps({
  variant: {
    type: String,
    default: "info",
    validator: (value) => ["success", "error", "warning", "info"].includes(value),
  },
  title: String,
  dismissible: Boolean,
});

const emit = defineEmits(["dismiss"]);

const classes = computed(() => {
  const map = {
    success: "bg-success-50 text-success-700 ring-success-600/20",
    error: "bg-danger-50 text-danger-700 ring-danger-600/20",
    warning: "bg-warning-50 text-warning-700 ring-warning-600/20",
    info: "bg-info-50 text-info-700 ring-info-600/20",
  };
  return map[props.variant];
});
</script>

<template>
  <div class="rounded-input p-4 ring-1 ring-inset" :class="classes" role="alert">
    <div class="flex items-start justify-between gap-3">
      <div>
        <p v-if="title" class="font-semibold">{{ title }}</p>
        <div class="text-sm" :class="title ? 'mt-1' : ''">
          <slot />
        </div>
      </div>
      <button
        v-if="dismissible"
        type="button"
        class="min-h-touch min-w-touch rounded p-1 text-current/70 hover:text-current"
        aria-label="Dismiss"
        @click="emit('dismiss')"
      >
        ✕
      </button>
    </div>
  </div>
</template>
