<script setup>
import { onMounted } from "vue";
import { StatCard } from "@/components/dashboard";
import StepUpModal from "@/components/system-control/StepUpModal.vue";
import { settingsRoutes as r } from "@/config/settingsRoutes";
import { systemControlNav } from "@/config/moduleNav";
import { useStepUp } from "@/composables/useStepUp";
import { useToast } from "@/composables/useToast";
import { LoadingSkeleton, ModuleNav, PageHeader, VAlert, VButton, VCard } from "@/components/ui";
import { useSystemControlStore } from "@/stores/systemControl";

const store = useSystemControlStore();
const toast = useToast();
const stepUp = useStepUp();

function formatBytes(bytes) {
  if (!bytes) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  let value = bytes;
  let i = 0;
  while (value >= 1024 && i < units.length - 1) {
    value /= 1024;
    i += 1;
  }
  return `${value.toFixed(1)} ${units[i]}`;
}

onMounted(() => store.fetchStorage().catch(() => {}));

function cleanup() {
  stepUp.requireStepUp(() =>
    store
      .cleanupStorage()
      .then((result) => toast.success(`Removed ${result.removed_files} files.`))
      .catch(() => {})
  );
}
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="Storage"
      subtitle="Disk, media, database, logs, and cache usage."
      :breadcrumbs="[{ label: 'Settings', to: r.overview }, { label: 'Advanced', to: r.advanced.hub }, { label: 'Storage' }]"
    />
    <ModuleNav :items="systemControlNav" />
    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>
    <LoadingSkeleton v-if="store.loading && !store.storage" variant="stats" :rows="4" />

    <template v-else-if="store.storage">
      <section class="grid grid-cols-1 gap-4 xs:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Media" :value="formatBytes(store.storage.media_bytes)" accent="brand" />
        <StatCard label="Logs" :value="formatBytes(store.storage.logs_bytes)" accent="slate" />
        <StatCard label="Database" :value="formatBytes(store.storage.database_bytes)" accent="green" />
        <StatCard label="Backups" :value="formatBytes(store.storage.backups_bytes)" accent="amber" />
      </section>
      <VCard title="Disk usage">
        <p v-if="store.storage.disk?.percent != null" class="text-sm">Used: {{ store.storage.disk.percent }}%</p>
        <VButton class="mt-4" variant="secondary" @click="cleanup">Clean rotated logs</VButton>
      </VCard>
    </template>

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
