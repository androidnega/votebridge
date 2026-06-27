<script setup>
import VBadge from "./VBadge.vue";

defineProps({
  status: {
    type: String,
    required: true,
  },
  label: {
    type: String,
    default: "",
  },
  size: {
    type: String,
    default: "md",
  },
});

const displayLabel = (status, label) =>
  label || status?.replace(/_/g, " ") || "unknown";
</script>

<template>
  <VBadge :variant="status" :size="size" dot>
    {{ displayLabel(status, label) }}
  </VBadge>
</template>
