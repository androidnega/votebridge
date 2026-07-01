<script setup>
import { onMounted, reactive } from "vue";
import StepUpModal from "@/components/system-control/StepUpModal.vue";
import { settingsRoutes as r } from "@/config/settingsRoutes";
import { systemControlNav } from "@/config/moduleNav";
import { useStepUp } from "@/composables/useStepUp";
import { useToast } from "@/composables/useToast";
import { LoadingSkeleton, ModuleNav, PageHeader, VAlert, VButton, VCard, VInput } from "@/components/ui";
import { useSystemControlStore } from "@/stores/systemControl";

const store = useSystemControlStore();
const toast = useToast();
const stepUp = useStepUp();
const form = reactive({
  read_only_mode: false,
  emergency_stop_voting: false,
  emergency_stop_results: false,
  disable_login: false,
  message: "",
  expected_return_at: "",
});

onMounted(async () => {
  const data = await store.fetchMaintenance().catch(() => null);
  if (data) Object.assign(form, { ...data, expected_return_at: data.expected_return_at || "" });
});

function save() {
  stepUp.requireStepUp(() =>
    store
      .saveMaintenance(form)
      .then(() => toast.success("Maintenance settings saved."))
      .catch(() => {})
  );
}
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="System Maintenance"
      subtitle="Configure maintenance messaging, emergency stops, and availability controls. Enable maintenance mode from Feature Flags."
      :breadcrumbs="[{ label: 'Settings', to: r.overview }, { label: 'Advanced', to: r.advanced.hub }, { label: 'Maintenance' }]"
    />
    <ModuleNav :items="systemControlNav" />
    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>
    <LoadingSkeleton v-if="store.loading && !store.maintenance" variant="list" :rows="6" />
    <VCard v-else title="Maintenance controls">
      <form class="space-y-4" @submit.prevent="save">
        <label v-for="field in ['read_only_mode','emergency_stop_voting','emergency_stop_results','disable_login']" :key="field" class="flex items-center gap-3 text-sm">
          <input v-model="form[field]" type="checkbox" class="h-4 w-4 rounded border-border" />
          <span>{{ field.replace(/_/g, ' ') }}</span>
        </label>
        <VInput v-model="form.message" label="Maintenance message" />
        <VInput v-model="form.expected_return_at" label="Expected return (ISO datetime)" />
        <VButton type="submit" variant="primary" :loading="store.actionLoading">Save (requires verification)</VButton>
      </form>
    </VCard>

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
