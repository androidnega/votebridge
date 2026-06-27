<script setup>
import { computed, onMounted, onUnmounted } from "vue";
import { ActivityFeed, ConnectionStatusIndicator, StatCard } from "@/components/dashboard";
import OpsHealthBadge from "@/components/operations/OpsHealthBadge.vue";
import { operationsNav } from "@/config/moduleNav";
import { EmptyState, LoadingSkeleton, ModuleNav, PageHeader, VAlert, VCard } from "@/components/ui";
import { useOperationsStore } from "@/stores/operations";

const store = useOperationsStore();

const healthStatus = computed(() => store.overview?.system_health?.status || "unknown");

onMounted(() => {
  store.fetchOverview().catch(() => {});
  store.connectRealtime();
});

onUnmounted(() => {
  store.disconnectRealtime();
});
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="Enterprise Operations Center"
      subtitle="Real-time platform monitoring for election operations."
      :breadcrumbs="[{ label: 'Overview', to: '/' }, { label: 'Operations' }]"
    >
      <template #actions>
        <ConnectionStatusIndicator :status="store.realtimeStatus" />
        <OpsHealthBadge :status="healthStatus" />
      </template>
    </PageHeader>

    <ModuleNav :items="operationsNav" aria-label="Operations navigation" />

    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>
    <LoadingSkeleton v-if="store.loading && !store.overview" variant="stats" :rows="8" />

    <template v-else-if="store.overview">
      <section class="grid grid-cols-1 gap-4 xs:grid-cols-2 lg:grid-cols-4 2xl:grid-cols-5">
        <StatCard label="System health" :value="healthStatus" accent="green" />
        <StatCard label="Open elections" :value="store.overview.elections?.open ?? 0" accent="brand" />
        <StatCard label="Active sessions" :value="store.overview.realtime?.authenticated_sessions ?? 0" accent="slate" />
        <StatCard label="Pending alerts" :value="store.overview.pending_workloads?.pending_security_alerts ?? 0" accent="amber" />
        <StatCard label="Pending fraud" :value="store.overview.pending_workloads?.pending_fraud_investigations ?? 0" accent="red" />
        <StatCard label="Certification queue" :value="store.overview.pending_workloads?.pending_certification ?? 0" accent="amber" />
        <StatCard label="SMS queue" :value="store.overview.communications_summary?.pending_queue ?? 0" accent="brand" />
        <StatCard label="USSD active" :value="store.overview.ussd_summary?.active_sessions ?? 0" accent="green" />
      </section>

      <section class="grid grid-cols-1 gap-4 lg:grid-cols-2 xl:grid-cols-3">
        <VCard title="Election status">
          <dl class="grid grid-cols-2 gap-3 text-sm">
            <div><dt class="text-slate-500">Scheduled</dt><dd class="font-semibold">{{ store.overview.elections?.scheduled ?? 0 }}</dd></div>
            <div><dt class="text-slate-500">Closed</dt><dd class="font-semibold">{{ store.overview.elections?.closed ?? 0 }}</dd></div>
            <div><dt class="text-slate-500">Archived</dt><dd class="font-semibold">{{ store.overview.elections?.archived ?? 0 }}</dd></div>
            <div><dt class="text-slate-500">Paused</dt><dd class="font-semibold">{{ store.overview.elections?.paused ?? 0 }}</dd></div>
          </dl>
        </VCard>

        <VCard title="Sessions by role">
          <dl class="grid grid-cols-2 gap-3 text-sm">
            <div><dt class="text-slate-500">Students</dt><dd class="font-semibold">{{ store.overview.sessions_by_role?.students ?? 0 }}</dd></div>
            <div><dt class="text-slate-500">Candidates</dt><dd class="font-semibold">{{ store.overview.sessions_by_role?.candidates ?? 0 }}</dd></div>
            <div><dt class="text-slate-500">Admins</dt><dd class="font-semibold">{{ store.overview.sessions_by_role?.admins ?? 0 }}</dd></div>
            <div><dt class="text-slate-500">Super admins</dt><dd class="font-semibold">{{ store.overview.sessions_by_role?.super_admins ?? 0 }}</dd></div>
          </dl>
        </VCard>

        <VCard title="Resource usage">
          <dl class="grid grid-cols-1 gap-3 text-sm">
            <div class="flex justify-between"><dt class="text-slate-500">CPU</dt><dd>{{ store.overview.resource_usage?.cpu_percent ?? "—" }}%</dd></div>
            <div class="flex justify-between"><dt class="text-slate-500">Memory</dt><dd>{{ store.overview.resource_usage?.memory_percent ?? "—" }}%</dd></div>
            <div class="flex justify-between"><dt class="text-slate-500">Storage</dt><dd>{{ store.overview.resource_usage?.disk_percent ?? "—" }}%</dd></div>
          </dl>
        </VCard>
      </section>

      <ActivityFeed
        title="Recent operational events"
        :items="store.liveEvents.slice(0, 8)"
        :loading="false"
        empty-title="Awaiting live events"
        empty-description="Operational websocket events will stream here."
      />
    </template>

    <EmptyState v-else title="Operations data unavailable" description="Connect to the API to load the operations center." icon="operations" />
  </div>
</template>
