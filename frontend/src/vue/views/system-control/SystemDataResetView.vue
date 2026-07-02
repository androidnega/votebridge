<script setup>
import { ref } from "vue";
import StepUpModal from "@/components/system-control/StepUpModal.vue";
import SystemSectionCard from "@/components/system-control/SystemSectionCard.vue";
import { ConfirmDialog, ModuleNav, PageHeader, VAlert, VButton, VInput } from "@/components/ui";
import { settingsNav } from "@/config/moduleNav";
import { settingsRoutes as r } from "@/config/settingsRoutes";
import { toastMessages } from "@/config/toastMessages";
import { useStepUp } from "@/composables/useStepUp";
import { useToast } from "@/composables/useToast";
import { useSystemControlStore } from "@/stores/systemControl";

const RESET_PHRASE = "RESET OPERATIONAL DATA";

const store = useSystemControlStore();
const toast = useToast();
const stepUp = useStepUp();

const confirmation = ref("");
const confirmOpen = ref(false);
const lastSummary = ref(null);

function openResetFlow() {
  if (confirmation.value.trim() !== RESET_PHRASE) {
    toast.error(`Type "${RESET_PHRASE}" to continue.`);
    return;
  }
  confirmOpen.value = true;
}

async function runReset() {
  confirmOpen.value = false;
  await stepUp.requireStepUp(async () => {
    try {
      lastSummary.value = await store.resetOperationalData(confirmation.value.trim());
      confirmation.value = "";
      toast.success(toastMessages.system.dataReset);
    } catch {
      toast.error(store.error || toastMessages.generic.error);
    }
  });
}
</script>

<template>
  <div class="vb-page space-y-section">
    <PageHeader
      title="Operational data reset"
      subtitle="Remove all elections, votes, results, and related operational records. User accounts and platform settings are kept."
      :breadcrumbs="[
        { label: 'Settings', to: r.overview },
        { label: 'Advanced', to: r.advanced.hub },
        { label: 'Data reset' },
      ]"
    />

    <ModuleNav :items="settingsNav" aria-label="Settings sections" />

    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>

    <SystemSectionCard
      section-id="data-reset"
      title="Reset election platform data"
      description="Use when demo data needs to be cleared or the environment should start fresh. This cannot be undone."
      icon="operations"
      :items="[]"
    >
      <div class="space-y-4">
        <p class="text-sm text-slate-600">
          This removes every election, vote, result, ballot seal, SVT token, fraud case, and election notification.
          Administrator accounts, students, institution settings, and integrations remain intact.
        </p>

        <VInput
          v-model="confirmation"
          label='Confirmation phrase'
          :placeholder="RESET_PHRASE"
          hint='Type the phrase exactly as shown to enable reset.'
        />

        <VButton variant="danger" :loading="store.actionLoading" @click="openResetFlow">
          Reset operational data
        </VButton>

        <div
          v-if="lastSummary"
          class="rounded-lg border border-border bg-surface-muted/60 p-4 text-sm text-slate-700"
        >
          <p class="font-semibold text-slate-900">Last reset summary</p>
          <ul class="mt-2 space-y-1">
            <li>Elections removed: {{ lastSummary.elections_removed }}</li>
            <li>Votes removed: {{ lastSummary.votes_removed }}</li>
            <li>Results removed: {{ lastSummary.results_removed }}</li>
            <li>Notifications removed: {{ lastSummary.notifications_removed }}</li>
          </ul>
        </div>
      </div>
    </SystemSectionCard>

    <ConfirmDialog
      v-model="confirmOpen"
      title="Reset all operational data?"
      description="Every election and voting record will be permanently deleted. User accounts and system configuration will not be affected."
      variant="danger"
      icon="fraud"
      confirm-label="Reset now"
      :loading="store.actionLoading"
      @confirm="runReset"
    />

    <StepUpModal
      v-model="stepUp.modalOpen"
      v-model:otp-code="stepUp.otpCode"
      :verifying="stepUp.verifying"
      :requesting="stepUp.requesting"
      @verify="stepUp.verifyAndContinue()"
      @resend="stepUp.requestChallenge()"
    />
  </div>
</template>
