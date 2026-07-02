<script setup>
import { onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import OpsHealthBadge from "@/components/operations/OpsHealthBadge.vue";
import { useSettingsIntegrations } from "@/composables/useSettingsIntegrations";
import { useToast } from "@/composables/useToast";
import { settingsRoutes as r } from "@/config/settingsRoutes";
import { settingsNav } from "@/config/moduleNav";
import { LoadingSkeleton, ModuleNav, PageHeader, SectionHeader, VAlert, VButton, VCard } from "@/components/ui";

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

const configLinks = [
  { title: "SMS providers", description: "Arkesel and Moolre credentials.", to: r.integrations.sms },
  { title: "Email providers", description: "SMTP delivery configuration.", to: r.integrations.email },
  { title: "USSD gateway", description: "Callback URL and session limits.", to: r.integrations.ussd },
  { title: "All providers", description: "Combined provider management.", to: r.integrations.providers },
  { title: "Notifications", description: "Templates and delivery rules.", to: r.integrations.notifications },
];
</script>

<template>
  <div class="vb-page space-y-section">
    <PageHeader
      title="Integrations"
      subtitle="Provider configuration, credentials, and integration health."
      :breadcrumbs="[{ label: 'Settings', to: r.overview }, { label: 'Integrations' }]"
    />
    <ModuleNav :items="settingsNav" />
    <VAlert v-if="error" variant="error">{{ error }}</VAlert>

    <section aria-label="Integration configuration">
      <SectionHeader
        title="Provider configuration"
        subtitle="Credentials, callbacks, and delivery settings — feature toggles live in Feature Flags."
      />
      <div class="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <VCard v-for="link in configLinks" :key="link.to" :title="link.title">
          <p class="text-sm text-slate-600">{{ link.description }}</p>
          <VButton class="mt-4" size="sm" variant="secondary" @click="router.push(link.to)">
            Configure
          </VButton>
        </VCard>
      </div>
    </section>

    <section aria-label="Integration health">
      <SectionHeader title="Integration health" subtitle="Live connectivity status and validation." />

      <LoadingSkeleton v-if="loading" variant="list" :rows="5" class="mt-4" />

      <div v-else class="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-2">
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
    </section>
  </div>
</template>
