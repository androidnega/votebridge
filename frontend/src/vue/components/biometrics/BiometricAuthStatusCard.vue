<script setup>
import { computed, onMounted } from "vue";
import { StatusBadge, VCard } from "@/components/ui";
import { useBiometricsStore } from "@/stores/biometrics";

const biometricsStore = useBiometricsStore();

onMounted(() => {
  biometricsStore.fetchStatus().catch(() => {});
});

const authEnabled = computed(() => Boolean(biometricsStore.status?.auth_enabled));
const moduleEnabled = computed(() => Boolean(biometricsStore.status?.module_enabled));

const statusLabel = computed(() => {
  if (!authEnabled.value) return "Disabled";
  if (moduleEnabled.value) return "Enabled";
  return "Configured off";
});

const statusVariant = computed(() => {
  if (!authEnabled.value) return "draft";
  if (moduleEnabled.value) return "open";
  return "paused";
});

const message = computed(
  () =>
    biometricsStore.status?.deployment_message ||
    "Biometric authentication is currently disabled for this deployment and can be enabled in a future release."
);
</script>

<template>
  <VCard title="Biometric Authentication" class="mt-section">
    <div class="vb-bio-auth-status">
      <div class="vb-bio-auth-status__row">
        <span class="vb-bio-auth-status__label">Status</span>
        <StatusBadge :status="statusVariant" :label="statusLabel" />
      </div>
      <p class="vb-bio-auth-status__message">
        {{ message }}
      </p>
      <p v-if="authEnabled && !moduleEnabled" class="vb-bio-auth-status__hint">
        The module is available but the <code>future_biometrics</code> feature flag is off.
      </p>
    </div>
  </VCard>
</template>

<style scoped>
.vb-bio-auth-status {
  @apply space-y-3;
}

.vb-bio-auth-status__row {
  @apply flex items-center justify-between gap-3;
}

.vb-bio-auth-status__label {
  @apply text-sm font-medium text-slate-700;
}

.vb-bio-auth-status__message {
  @apply text-sm text-slate-600;
}

.vb-bio-auth-status__hint {
  @apply text-xs text-slate-500;
}
</style>
