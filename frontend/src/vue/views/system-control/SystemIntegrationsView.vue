<script setup>
import { onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import OpsHealthBadge from "@/components/operations/OpsHealthBadge.vue";
import { useSettingsIntegrations } from "@/composables/useSettingsIntegrations";
import { useToast } from "@/composables/useToast";
import { settingsRoutes as r } from "@/config/settingsRoutes";
import { settingsNav } from "@/config/moduleNav";
import { LoadingSkeleton, ModuleNav, PageHeader, VAlert, VButton, VCard } from "@/components/ui";

const route = useRoute();
const router = useRouter();
const toast = useToast();

const {
  loading,
  error,
  testingKey,
  integrations,
  normalizeHealthStatus,
  formatTimestamp,
  load,
  validateConnection,
} = useSettingsIntegrations();

onMounted(() => {
  load().then(() => {
    const focus = route.query.focus;
    if (focus) {
      document.getElementById(`integration-${focus}`)?.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  });
});

async function validate(integration) {
  try {
    const result = await validateConnection(integration);
    toast.success(result?.message || "Connection validation completed.");
    await load();
  } catch {
    toast.error("Connection validation failed.");
  }
}
</script>

<template>
  <div class="vb-page space-y-section">
    <PageHeader
      title="Integrations"
      subtitle="Communication providers and infrastructure connectivity for the platform."
      :breadcrumbs="[{ label: 'Settings', to: r.overview }, { label: 'Integrations' }]"
    />
    <ModuleNav :items="settingsNav" />
    <VAlert v-if="error" variant="error">{{ error }}</VAlert>

    <LoadingSkeleton v-if="loading" variant="list" :rows="5" />

    <div v-else class="grid grid-cols-1 gap-4 lg:grid-cols-2">
      <VCard
        v-for="integration in integrations"
        :id="`integration-${integration.key}`"
        :key="integration.key"
        :title="integration.name"
      >
        <div class="space-y-3 text-sm">
          <div class="flex flex-wrap items-center gap-2">
            <span class="text-xs font-semibold uppercase tracking-wide text-slate-500">Status</span>
            <OpsHealthBadge :status="normalizeHealthStatus(integration.status)" />
          </div>
          <div>
            <p class="text-xs font-semibold uppercase tracking-wide text-slate-500">Last sync</p>
            <p class="mt-0.5 text-slate-700">{{ formatTimestamp(integration.lastSync) }}</p>
          </div>
          <div>
            <p class="text-xs font-semibold uppercase tracking-wide text-slate-500">Last error</p>
            <p class="mt-0.5 text-slate-700">{{ integration.lastError || "None recorded" }}</p>
          </div>
        </div>
        <div class="mt-4 flex flex-wrap gap-2">
          <VButton
            size="sm"
            variant="secondary"
            :loading="testingKey === integration.key"
            @click="validate(integration)"
          >
            Validate connection
          </VButton>
          <VButton size="sm" variant="ghost" @click="router.push(integration.configRoute)">
            Configuration
          </VButton>
        </div>
      </VCard>
    </div>
  </div>
</template>
