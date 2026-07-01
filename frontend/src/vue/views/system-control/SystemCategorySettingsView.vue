<script setup>
import { computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import SettingsForm from "@/components/system-control/SettingsForm.vue";
import StepUpModal from "@/components/system-control/StepUpModal.vue";
import BiometricResetPanel from "@/components/biometrics/BiometricResetPanel.vue";
import BiometricAuthStatusCard from "@/components/biometrics/BiometricAuthStatusCard.vue";
import { settingsRoutes as r } from "@/config/settingsRoutes";
import { systemControlNav } from "@/config/moduleNav";
import { useStepUp } from "@/composables/useStepUp";
import { useToast } from "@/composables/useToast";
import { toastMessages } from "@/config/toastMessages";
import { LoadingSkeleton, ModuleNav, PageHeader, VAlert, VButton, VCard, VInput } from "@/components/ui";
import { useSystemControlStore } from "@/stores/systemControl";

const props = defineProps({
  category: { type: String, required: true },
  title: { type: String, required: true },
  subtitle: { type: String, default: "" },
  sensitive: { type: Boolean, default: false },
});

const route = useRoute();
const store = useSystemControlStore();
const toast = useToast();
const stepUp = useStepUp();

const breadcrumbs = computed(() => {
  const path = route.path;
  if (path.includes("/integrations/")) {
    return [
      { label: "Settings", to: r.overview },
      { label: "Integrations", to: r.integrations.hub },
      { label: props.title },
    ];
  }
  if (path.includes("/security/")) {
    return [
      { label: "Settings", to: r.overview },
      { label: "Security", to: r.security.hub },
      { label: props.title },
    ];
  }
  return [{ label: "Settings", to: r.overview }, { label: props.title }];
});

const items = computed(() => store.settings[props.category] || []);

onMounted(() => {
  store.fetchSettings(props.category).catch(() => {});
});

function save(updates) {
  const run = () =>
    store
      .saveSettings(props.category, updates)
      .then(() => toast.success(toastMessages.settings.saved))
      .catch(() => {});

  if (props.sensitive) {
    stepUp.requireStepUp(run);
  } else {
    run();
  }
}
</script>

<template>
  <div class="vb-page">
    <PageHeader
      :title="title"
      :subtitle="subtitle || `Manage ${title.toLowerCase()} configuration.`"
      :breadcrumbs="breadcrumbs"
    />
    <ModuleNav :items="systemControlNav" />
    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>
    <LoadingSkeleton v-if="store.loading && !items.length" variant="list" :rows="6" />
    <VCard v-else :title="title">
      <SettingsForm :items="items" :loading="store.actionLoading" :sensitive="sensitive" @save="save" />
    </VCard>

    <BiometricAuthStatusCard v-if="category === 'identity_assurance'" />
    <BiometricResetPanel v-if="category === 'identity_assurance'" />

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
