<script setup>
import { onMounted } from "vue";
import StepUpModal from "@/components/system-control/StepUpModal.vue";
import { settingsRoutes as r } from "@/config/settingsRoutes";
import { systemControlNav } from "@/config/moduleNav";
import { useStepUp } from "@/composables/useStepUp";
import { useToast } from "@/composables/useToast";
import { LoadingSkeleton, ModuleNav, PageHeader, StatusBadge, VAlert, VButton, VCard, VTable } from "@/components/ui";
import { useSystemControlStore } from "@/stores/systemControl";

const store = useSystemControlStore();
const toast = useToast();
const stepUp = useStepUp();

const columns = [
  { key: "filename", label: "File" },
  { key: "status", label: "Status" },
  { key: "size_bytes", label: "Size" },
  { key: "created_at", label: "Created" },
];

onMounted(() => store.fetchBackups().catch(() => {}));

function createBackup() {
  stepUp.requireStepUp(() =>
    store
      .createBackup()
      .then(() => toast.success("Backup created."))
      .catch(() => {})
  );
}

function verify(uuid) {
  store.verifyBackup(uuid).then(() => toast.success("Backup verified.")).catch(() => {});
}

function formatRows(rows) {
  return rows.map((row) => ({
    ...row,
    size_bytes: row.size_bytes ? `${(row.size_bytes / 1024).toFixed(1)} KB` : "—",
    created_at: new Date(row.created_at).toLocaleString(),
  }));
}
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="Backup & Recovery"
      subtitle="Create, verify, and manage configuration backups."
      :breadcrumbs="[{ label: 'Settings', to: r.overview }, { label: 'Advanced', to: r.advanced.hub }, { label: 'Backup & recovery' }]"
    >
      <template #actions>
        <VButton variant="primary" @click="createBackup">Create backup</VButton>
      </template>
    </PageHeader>
    <ModuleNav :items="systemControlNav" />
    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>
    <LoadingSkeleton v-if="store.loading && !store.backups.length" variant="list" :rows="5" />
    <VCard v-else title="Backup history">
      <VTable :columns="columns" :rows="formatRows(store.backups)" empty-text="No backups yet." />
      <div v-if="store.backups.length" class="mt-4 flex flex-wrap gap-2">
        <VButton
          v-for="backup in store.backups.slice(0, 3)"
          :key="backup.uuid"
          size="sm"
          variant="secondary"
          @click="verify(backup.uuid)"
        >
          Verify {{ backup.filename }}
        </VButton>
      </div>
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
