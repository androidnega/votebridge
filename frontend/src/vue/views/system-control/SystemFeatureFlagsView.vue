<script setup>
import { onMounted } from "vue";
import StepUpModal from "@/components/system-control/StepUpModal.vue";
import { systemControlNav } from "@/config/moduleNav";
import { useStepUp } from "@/composables/useStepUp";
import { useToast } from "@/composables/useToast";
import { LoadingSkeleton, ModuleNav, PageHeader, StatusBadge, VAlert, VButton, VCard } from "@/components/ui";
import { useSystemControlStore } from "@/stores/systemControl";

const store = useSystemControlStore();
const toast = useToast();
const stepUp = useStepUp();

onMounted(() => store.fetchFeatureFlags().catch(() => {}));

function toggleFlag(flag) {
  stepUp.requireStepUp(() =>
    store
      .toggleFeatureFlag(flag.key, !flag.enabled)
      .then(() => toast.success(`${flag.name} updated.`))
      .catch(() => {})
  );
}
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="Feature Flags"
      subtitle="Enable or disable platform modules without code changes."
      :breadcrumbs="[{ label: 'Overview', to: '/' }, { label: 'System Control', to: '/system-control' }, { label: 'Feature Flags' }]"
    />
    <ModuleNav :items="systemControlNav" />
    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>
    <LoadingSkeleton v-if="store.loading && !store.featureFlags.length" variant="list" :rows="8" />

    <div v-else class="grid grid-cols-1 gap-4 lg:grid-cols-2">
      <VCard v-for="flag in store.featureFlags" :key="flag.key" :title="flag.name">
        <p class="text-sm text-slate-600">{{ flag.description }}</p>
        <div class="mt-3 flex items-center justify-between">
          <StatusBadge :status="flag.enabled ? 'open' : 'closed'" />
          <VButton size="sm" variant="secondary" @click="toggleFlag(flag)">Toggle</VButton>
        </div>
        <p class="mt-2 text-xs text-slate-500">Last changed: {{ flag.last_changed_by || '—' }}</p>
      </VCard>
    </div>

    <StepUpModal
      v-model="stepUp.modalOpen.value"
      :otp-code="stepUp.otpCode.value"
      :verifying="stepUp.verifying.value"
      :requesting="stepUp.requesting.value"
      @update:otp-code="stepUp.otpCode.value = $event"
      @verify="stepUp.verifyAndContinue()"
      @resend="stepUp.requestChallenge()"
    />
  </div>
</template>
