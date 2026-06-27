<script setup>
import { computed, onMounted } from "vue";
import SettingsForm from "@/components/system-control/SettingsForm.vue";
import StepUpModal from "@/components/system-control/StepUpModal.vue";
import { systemControlNav } from "@/config/moduleNav";
import { useStepUp } from "@/composables/useStepUp";
import { useToast } from "@/composables/useToast";
import { LoadingSkeleton, ModuleNav, PageHeader, VAlert, VButton, VCard, VInput } from "@/components/ui";
import { useSystemControlStore } from "@/stores/systemControl";

const props = defineProps({
  category: { type: String, required: true },
  title: { type: String, required: true },
  subtitle: { type: String, default: "" },
  sensitive: { type: Boolean, default: false },
});

const store = useSystemControlStore();
const toast = useToast();
const stepUp = useStepUp();
const preview = ref(null);

const items = computed(() => store.settings[props.category] || []);

onMounted(() => {
  store.fetchSettings(props.category).catch(() => {});
});

function save(updates) {
  const run = () =>
    store
      .saveSettings(props.category, updates)
      .then(() => toast.success("Settings saved."))
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
      :breadcrumbs="[{ label: 'Overview', to: '/' }, { label: 'System Control', to: '/system-control' }, { label: title }]"
    />
    <ModuleNav :items="systemControlNav" />
    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>
    <LoadingSkeleton v-if="store.loading && !items.length" variant="list" :rows="6" />
    <VCard v-else :title="title">
      <SettingsForm :items="items" :loading="store.actionLoading" :sensitive="sensitive" @save="save" />
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
