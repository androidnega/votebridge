<script setup>
import { onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import { ConnectionStatusIndicator, EmptyState, StatCard } from "@/components/dashboard";
import { ussdNav } from "@/config/moduleNav";
import { LoadingSkeleton, ModuleNav, PageHeader, VAlert, VButton, VCard } from "@/components/ui";
import { useUssdStore } from "@/stores/ussd";

const router = useRouter();
const store = useUssdStore();

onMounted(() => {
  store.fetchDashboard().catch(() => {});
  store.connectRealtime();
});

onUnmounted(() => {
  store.disconnectRealtime();
});
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="USSD management"
      subtitle="Arkesel USSD sessions, votes, and provider status."
      :breadcrumbs="[{ label: 'Overview', to: '/' }, { label: 'USSD' }]"
    >
      <template #actions>
        <ConnectionStatusIndicator :status="store.realtimeStatus" />
        <VButton variant="secondary" size="sm" @click="router.push('/ussd/sessions')">
          Session monitor
        </VButton>
      </template>
    </PageHeader>

    <ModuleNav :items="ussdNav" aria-label="USSD navigation" />

    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>
    <LoadingSkeleton v-if="store.loading && !store.dashboard" variant="card" />

    <template v-else-if="store.dashboard">
      <section class="grid grid-cols-1 gap-4 xs:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Active sessions" :value="store.dashboard.active_sessions ?? 0" accent="brand" />
        <StatCard label="Completed votes" :value="store.dashboard.completed_votes ?? 0" accent="green" />
        <StatCard label="Abandoned" :value="store.dashboard.abandoned_sessions ?? 0" accent="amber" />
        <StatCard label="Failed sessions" :value="store.dashboard.failed_sessions ?? 0" accent="red" />
        <StatCard label="Successful requests" :value="store.dashboard.successful_requests ?? 0" accent="green" />
        <StatCard label="Failed requests" :value="store.dashboard.failed_requests ?? 0" accent="red" />
        <StatCard label="Requests today" :value="store.dashboard.requests_today ?? 0" accent="slate" />
        <StatCard
          label="Avg session (sec)"
          :value="Math.round(store.dashboard.average_session_seconds ?? 0)"
          accent="slate"
        />
      </section>

      <VCard title="Configuration status">
        <dl class="grid grid-cols-1 gap-3 text-sm sm:grid-cols-2">
          <div class="flex justify-between gap-4 rounded-input bg-surface-muted px-4 py-3">
            <dt class="text-slate-500">Provider</dt>
            <dd class="font-medium capitalize text-slate-800">{{ store.dashboard.provider_status }}</dd>
          </div>
          <div class="flex justify-between gap-4 rounded-input bg-surface-muted px-4 py-3">
            <dt class="text-slate-500">SMS confirmations</dt>
            <dd class="font-medium text-slate-800">{{ store.dashboard.sms_sent ?? 0 }} sent</dd>
          </div>
          <div class="flex justify-between gap-4 rounded-input bg-surface-muted px-4 py-3">
            <dt class="text-slate-500">Callback endpoint</dt>
            <dd class="font-medium text-slate-800">/api/v1/ussd/callback/</dd>
          </div>
          <div class="flex justify-between gap-4 rounded-input bg-surface-muted px-4 py-3">
            <dt class="text-slate-500">Expired sessions</dt>
            <dd class="font-medium text-slate-800">{{ store.dashboard.expired_sessions ?? 0 }}</dd>
          </div>
        </dl>
      </VCard>
    </template>

    <EmptyState
      v-else
      title="USSD dashboard unavailable"
      description="Connect to the API and ensure migrations are applied."
      icon="ussd"
    />
  </div>
</template>
