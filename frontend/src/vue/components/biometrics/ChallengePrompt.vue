<script setup>
import { computed } from "vue";
import { VCard } from "@/components/ui";

const props = defineProps({
  challenge: { type: Object, default: null },
  loading: { type: Boolean, default: false },
});

const instruction = computed(
  () => props.challenge?.instruction || "Follow the on-screen identity challenge."
);
</script>

<template>
  <VCard title="Identity challenge" class="text-center">
    <p class="text-lg font-medium text-brand">{{ instruction }}</p>
    <p v-if="loading" class="mt-2 text-sm text-slate-600">Verifying…</p>
    <p v-else class="mt-2 text-sm text-slate-600">
      Complete the action while facing the camera. Do not use photos or screens.
    </p>
    <slot />
  </VCard>
</template>
