<script setup>
import { computed } from "vue";

const props = defineProps({
  status: {
    type: String,
    default: "disconnected",
  },
  label: {
    type: String,
    default: "",
  },
});

const displayLabel = computed(() => {
  if (props.label) return props.label;
  return (
    {
      connected: "Live",
      connecting: "Connecting",
      disconnected: "Offline",
      error: "Error",
    }[props.status] || "Live"
  );
});

const badgeClass = computed(() => ({
  "bg-green-50 text-green-700 ring-green-200": props.status === "connected",
  "bg-amber-50 text-amber-700 ring-amber-200": props.status === "connecting",
  "bg-slate-100 text-slate-600 ring-slate-200": props.status === "disconnected",
  "bg-red-50 text-red-700 ring-red-200": props.status === "error",
}));

const dotClass = computed(() => ({
  "bg-green-500 animate-pulse": props.status === "connected",
  "bg-amber-500 animate-pulse": props.status === "connecting",
  "bg-slate-400": props.status === "disconnected",
  "bg-red-500": props.status === "error",
}));
</script>

<template>
  <span
    class="inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset"
    :class="badgeClass"
    role="status"
    :aria-label="`Connection status: ${displayLabel}`"
  >
    <span class="h-1.5 w-1.5 rounded-full" :class="dotClass" />
    <span>{{ displayLabel }}</span>
  </span>
</template>
