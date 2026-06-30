<script setup>
import { onMounted } from "vue";
import StepUpModal from "@/components/system-control/StepUpModal.vue";
import OpsHealthBadge from "@/components/operations/OpsHealthBadge.vue";
import { systemControlNav } from "@/config/moduleNav";
import { useStepUp } from "@/composables/useStepUp";
import { useToast } from "@/composables/useToast";
import { LoadingSkeleton, ModuleNav, PageHeader, StatusBadge, VAlert, VButton, VCard } from "@/components/ui";
import { useSystemControlStore } from "@/stores/systemControl";

const props = defineProps({
  providerType: { type: String, default: "" },
  title: { type: String, default: "Communication Providers" },
});

const store = useSystemControlStore();
const toast = useToast();
const stepUp = useStepUp();

onMounted(() => {
  store.fetchProviders(props.providerType || undefined).catch(() => {});
});

function testProvider(uuid) {
  store
    .testProvider(uuid)
    .then((result) => toast.success(result.message || "Connection test completed."))
    .catch(() => {});
}

function editProvider(provider) {
  stepUp.requireStepUp(() =>
    store
      .saveProvider(provider.uuid, { is_active: !provider.is_active })
      .then(() => {
        toast.success("Provider updated.");
        store.fetchProviders(props.providerType || undefined);
      })
      .catch(() => {})
  );
}
</script>

<template>
  <div class="vb-page">
    <PageHeader
      :title="title"
      subtitle="Manage provider connections, credentials, and priority."
      :breadcrumbs="[{ label: 'Dashboard', to: '/dashboard' }, { label: 'System Control', to: '/dashboard/system-control' }, { label: title }]"
    />
    <ModuleNav :items="systemControlNav" />
    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>
    <LoadingSkeleton v-if="store.loading && !store.providers.length" variant="list" :rows="4" />

    <div v-else class="grid grid-cols-1 gap-4 lg:grid-cols-2">
      <VCard v-for="provider in store.providers" :key="provider.uuid" :title="provider.name">
        <div class="space-y-2 text-sm">
          <p class="text-slate-500">{{ provider.provider_type }}</p>
          <OpsHealthBadge :status="provider.connection_status === 'connected' ? 'healthy' : 'warning'" />
          <StatusBadge :status="provider.is_active ? 'open' : 'closed'" />
        </div>
        <div class="mt-4 flex flex-wrap gap-2">
          <VButton size="sm" variant="secondary" @click="testProvider(provider.uuid)">Test connection</VButton>
          <VButton size="sm" variant="primary" @click="editProvider(provider)">
            {{ provider.is_active ? "Disable" : "Enable" }}
          </VButton>
        </div>
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
