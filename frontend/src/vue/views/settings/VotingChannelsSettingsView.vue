<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { ussdApi } from "@/api/ussd";
import { ModuleNav, PageHeader, VAlert, VButton, VCard, LoadingSkeleton } from "@/components/ui";
import { settingsNav } from "@/config/moduleNav";

const router = useRouter();

const integration = ref(null);
const loading = ref(false);
const error = ref(null);

const channels = [
  {
    title: "Web voting",
    description: "Browser-based voting policies and channel availability.",
    to: "/dashboard/settings/election-policies",
  },
  {
    title: "USSD voting",
    description: "Mobile USSD menu codes, session limits, and provider routing.",
    to: "/dashboard/settings/ussd",
  },
  {
    title: "SMS notifications",
    description: "SMS delivery settings and notification templates.",
    to: "/dashboard/settings/notifications",
  },
  {
    title: "Channel health",
    description: "Monitor USSD sessions, queues, and delivery performance.",
    to: "/dashboard/ussd",
  },
  {
    title: "Provider testing",
    description: "Send test messages and validate communication providers.",
    to: "/dashboard/communications/test",
  },
];

const healthStatusLabel = computed(() => {
  const status = integration.value?.health_status;
  return (
    {
      healthy: "Healthy",
      degraded: "Degraded",
      pending: "Pending",
      unconfigured: "Not configured",
    }[status] || "Unknown"
  );
});

const reachabilityLabel = computed(() => {
  const value = integration.value?.health?.reachable;
  return (
    {
      reachable: "Reachable",
      unreachable: "Unreachable",
      degraded: "Degraded",
      unconfigured: "Not configured",
    }[value] || "Unknown"
  );
});

function formatTimestamp(value) {
  if (!value) return "—";
  return new Date(value).toLocaleString();
}

onMounted(async () => {
  loading.value = true;
  error.value = null;
  try {
    integration.value = await ussdApi.getIntegration();
  } catch (err) {
    error.value = err?.message || "Failed to load USSD integration settings.";
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <div class="vb-page space-y-section">
    <PageHeader
      title="Voting channels"
      subtitle="Configure how students vote and receive election communications."
      :breadcrumbs="[{ label: 'Settings', to: '/dashboard/settings' }, { label: 'Voting channels' }]"
    />

    <ModuleNav :items="settingsNav" />

    <VAlert v-if="error" variant="error">{{ error }}</VAlert>

    <LoadingSkeleton v-if="loading && !integration" variant="card" />

    <template v-else-if="integration">
      <section class="grid grid-cols-1 gap-4 xl:grid-cols-2">
        <VCard title="USSD callback configuration" subtitle="Register this URL with Arkesel.">
          <dl class="space-y-3 text-sm">
            <div class="rounded-input border border-border bg-surface-muted px-4 py-3">
              <dt class="text-slate-500">Callback URL</dt>
              <dd class="mt-1 break-all font-medium text-slate-900">{{ integration.callback_url }}</dd>
            </div>
            <div class="flex justify-between gap-4 rounded-input bg-surface-muted px-4 py-3">
              <dt class="text-slate-500">Environment</dt>
              <dd class="font-medium capitalize text-slate-800">{{ integration.environment }}</dd>
            </div>
            <div class="flex justify-between gap-4 rounded-input bg-surface-muted px-4 py-3">
              <dt class="text-slate-500">Health status</dt>
              <dd class="font-medium text-slate-800">{{ healthStatusLabel }}</dd>
            </div>
            <div class="flex justify-between gap-4 rounded-input bg-surface-muted px-4 py-3">
              <dt class="text-slate-500">Provider user ID</dt>
              <dd class="font-medium text-slate-800">{{ integration.provider_user_id }}</dd>
            </div>
            <div class="flex justify-between gap-4 rounded-input bg-surface-muted px-4 py-3">
              <dt class="text-slate-500">Public base URL</dt>
              <dd class="break-all font-medium text-slate-800">
                {{ integration.public_base_url || "Not configured" }}
              </dd>
            </div>
          </dl>
        </VCard>

        <VCard title="USSD callback health" subtitle="Operational callback telemetry.">
          <dl class="space-y-3 text-sm">
            <div class="flex justify-between gap-4 rounded-input bg-surface-muted px-4 py-3">
              <dt class="text-slate-500">Reachability</dt>
              <dd class="font-medium text-slate-800">{{ reachabilityLabel }}</dd>
            </div>
            <div class="flex justify-between gap-4 rounded-input bg-surface-muted px-4 py-3">
              <dt class="text-slate-500">Last callback received</dt>
              <dd class="font-medium text-slate-800">
                {{ formatTimestamp(integration.health?.last_callback_at) }}
              </dd>
            </div>
            <div class="flex justify-between gap-4 rounded-input bg-surface-muted px-4 py-3">
              <dt class="text-slate-500">Last successful callback</dt>
              <dd class="font-medium text-slate-800">
                {{ formatTimestamp(integration.health?.last_successful_callback_at) }}
              </dd>
            </div>
            <div class="flex justify-between gap-4 rounded-input bg-surface-muted px-4 py-3">
              <dt class="text-slate-500">Last failed callback</dt>
              <dd class="font-medium text-slate-800">
                {{ formatTimestamp(integration.health?.last_failed_callback_at) }}
              </dd>
            </div>
            <div class="flex justify-between gap-4 rounded-input bg-surface-muted px-4 py-3">
              <dt class="text-slate-500">Last HTTP status</dt>
              <dd class="font-medium text-slate-800">{{ integration.health?.last_http_status ?? "—" }}</dd>
            </div>
            <div class="flex justify-between gap-4 rounded-input bg-surface-muted px-4 py-3">
              <dt class="text-slate-500">Last processing duration</dt>
              <dd class="font-medium text-slate-800">
                {{
                  integration.health?.last_processing_duration_ms != null
                    ? `${integration.health.last_processing_duration_ms} ms`
                    : "—"
                }}
              </dd>
            </div>
          </dl>
        </VCard>
      </section>
    </template>

    <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
      <VCard v-for="channel in channels" :key="channel.title" :title="channel.title">
        <p class="text-sm text-slate-600">{{ channel.description }}</p>
        <VButton class="mt-4" variant="secondary" size="sm" @click="router.push(channel.to)">
          Open
        </VButton>
      </VCard>
    </div>
  </div>
</template>
