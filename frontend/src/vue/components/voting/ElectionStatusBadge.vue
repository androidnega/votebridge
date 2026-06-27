<script setup>
import StatusBadge from "@/components/ui/StatusBadge.vue";

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
</script>

<template>
  <StatusBadge :status="status" :label="label" :size="size" />
</template>
