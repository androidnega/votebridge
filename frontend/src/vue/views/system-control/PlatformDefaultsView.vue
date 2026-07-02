<script setup>
import { computed, onMounted } from "vue";
import SettingsForm from "@/components/system-control/SettingsForm.vue";
import StepUpModal from "@/components/system-control/StepUpModal.vue";
import { platformDefaultGroups } from "@/config/platformDefaults";
import { settingsRoutes as r } from "@/config/settingsRoutes";
import { settingsNav } from "@/config/moduleNav";
import { useStepUp } from "@/composables/useStepUp";
import { useToast } from "@/composables/useToast";
import { toastMessages } from "@/config/toastMessages";
import { LoadingSkeleton, ModuleNav, PageHeader, VAlert, VCard } from "@/components/ui";
import { useSystemControlStore } from "@/stores/systemControl";

const store = useSystemControlStore();
const toast = useToast();
const stepUp = useStepUp();

const categories = [...new Set(platformDefaultGroups.map((group) => group.category))];

const groupedItems = computed(() =>
  platformDefaultGroups.map((group) => ({
    ...group,
    items: (store.settings[group.category] || []).filter((item) => {
      const shortKey = item.key.includes(".") ? item.key.split(".").slice(1).join(".") : item.key;
      return group.keys.includes(shortKey);
    }),
  }))
);

const isLoading = computed(() => store.loading && categories.some((category) => !store.settings[category]?.length));

onMounted(async () => {
  await Promise.all(categories.map((category) => store.fetchSettings(category).catch(() => {})));
});

function saveGroup(group, updates) {
  const run = () =>
    store
      .saveSettings(group.category, updates)
      .then(() => toast.success(toastMessages.settings.saved))
      .catch(() => {});

  stepUp.requireStepUp(run);
}
</script>

<template>
  <div class="vb-page space-y-section">
    <PageHeader
      title="Platform defaults"
      subtitle="System-wide defaults applied when Election Administrators create elections. Individual election rules are configured in the Election workspace."
      :breadcrumbs="[{ label: 'Settings', to: r.overview }, { label: 'Election Governance', to: r.governance.hub }, { label: 'Platform defaults' }]"
    />
    <ModuleNav :items="settingsNav" />
    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>

    <LoadingSkeleton v-if="isLoading" variant="list" :rows="8" />

    <div v-else class="space-y-section">
      <VCard
        v-for="group in groupedItems"
        :key="group.id"
        :title="group.title"
        :subtitle="group.description"
      >
        <SettingsForm
          v-if="group.items.length"
          :items="group.items"
          :loading="store.actionLoading"
          sensitive
          @save="(values) => saveGroup(group, values)"
        />
        <p v-else class="text-sm text-slate-500">No defaults configured for this group yet.</p>
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
