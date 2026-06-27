<script setup>
import { computed } from "vue";
import { VAlert } from "@/components/ui";

const props = defineProps({
  reasons: { type: Array, default: () => [] },
  riskScore: { type: Number, default: null },
});

const visible = computed(() => props.reasons?.length > 0);

const message = computed(() => {
  if (props.riskScore != null && props.riskScore >= 70) {
    return "Additional identity verification is required due to elevated login risk.";
  }
  return "Identity verification is required for this login.";
});
</script>

<template>
  <VAlert v-if="visible" variant="warning" title="Security check required">
    <p>{{ message }}</p>
    <ul v-if="reasons.length" class="mt-2 list-disc pl-5 text-sm">
      <li v-for="reason in reasons" :key="reason">{{ reason.replaceAll("_", " ") }}</li>
    </ul>
  </VAlert>
</template>
