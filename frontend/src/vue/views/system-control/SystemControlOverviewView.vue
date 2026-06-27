<script setup>
import { onMounted } from "vue";
import { StatCard } from "@/components/dashboard";
import OpsHealthBadge from "@/components/operations/OpsHealthBadge.vue";
import { systemControlNav } from "@/config/moduleNav";
import { LoadingSkeleton, ModuleNav, PageHeader, VAlert, VCard } from "@/components/ui";
import { useSystemControlStore } from "@/stores/systemControl";

const store = useSystemControlStore();

onMounted(() => {
  store.fetchOverview().catch(() => {});
});
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="System Control Center"
      subtitle="Central administration for VoteBridge platform configuration."
      :breadcrumbs="[{ label: 'Overview', to: '/' }, { label: 'System Control' }]"
    />
    <ModuleNav :items="systemControlNav" aria-label="System Control navigation" />
    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>
    <LoadingSkeleton v-if="store.loading && !store.overview" variant="stats" :rows="6" />

    <template v-else-if="store.overview">
      <section class="grid grid-cols-1 gap-4 xs:grid-cols-2 lg:grid-cols-4 2xl:grid-cols-5">
        <StatCard label="System status" :value="store.overview.system_status" accent="green" />
        <StatCard label="Environment" :value="store.overview.environment" accent="slate" />
        <StatCard label="Version" :value="store.overview.application_version" accent="brand" />
        <StatCard label="Institution" :value="store.overview.institution" accent="brand" />
        <StatCard label="Active election" :value="store.overview.active_election || 'None'" accent="amber" />
      </section>

      <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <VCard title="Infrastructure status">
          <dl class="grid grid-cols-2 gap-3 text-sm">
            <div><dt class="text-slate-500">Database</dt><dd><OpsHealthBadge :status="store.overview.database_status" /></dd></div>
            <div><dt class="text-slate-500">Redis</dt><dd><OpsHealthBadge :status="store.overview.redis_status" /></dd></div>
            <div><dt class="text-slate-500">WebSockets</dt><dd><OpsHealthBadge :status="store.overview.websocket_status" /></dd></div>
            <div><dt class="text-slate-500">SMS</dt><dd>{{ store.overview.sms_provider }}</dd></div>
            <div><dt class="text-slate-500">Email</dt><dd>{{ store.overview.email_provider }}</dd></div>
            <div><dt class="text-slate-500">USSD</dt><dd><OpsHealthBadge :status="store.overview.ussd_provider" /></dd></div>
          </dl>
        </VCard>
        <VCard title="Maintenance">
          <p class="text-sm text-slate-600">{{ store.overview.maintenance_status?.message || "No maintenance scheduled." }}</p>
          <OpsHealthBadge
            class="mt-3 inline-flex"
            :status="store.overview.maintenance_status?.is_enabled ? 'warning' : 'healthy'"
          />
          <p v-if="store.overview.last_backup" class="mt-4 text-xs text-slate-500">Last backup: {{ new Date(store.overview.last_backup).toLocaleString() }}</p>
        </VCard>
      </div>

      <VCard title="Quick actions">
        <ul class="grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-4">
          <li v-for="action in store.overview.quick_actions" :key="action.action">
            <router-link
              :to="action.action === 'open_operations' ? '/operations' : '/system-control/maintenance'"
              class="block rounded-input border border-border px-4 py-3 text-sm font-medium text-brand hover:bg-surface-muted"
            >
              {{ action.label }}
            </router-link>
          </li>
        </ul>
      </VCard>
    </template>
  </div>
</template>
