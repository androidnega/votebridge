<script setup>
import { onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import { ConnectionStatusIndicator, StatCard } from "@/components/dashboard";
import { communicationsNav } from "@/config/moduleNav";
import {
  EmptyState,
  LoadingSkeleton,
  ModuleNav,
  PageHeader,
  VAlert,
  VButton,
  VCard,
} from "@/components/ui";
import { useNotificationsStore } from "@/stores/notifications";

const router = useRouter();
const store = useNotificationsStore();

onMounted(() => {
  store.fetchDashboard().catch(() => {});
  store.connectRealtime(true);
});

onUnmounted(() => {
  store.disconnectRealtime(true);
});
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="Communication center"
      subtitle="Central hub for SMS, email, and in-app notifications."
      :breadcrumbs="[{ label: 'Overview', to: '/' }, { label: 'Communications' }]"
    >
      <template #actions>
        <ConnectionStatusIndicator :status="store.realtimeStatus" />
      </template>
    </PageHeader>

    <ModuleNav :items="communicationsNav" aria-label="Communications navigation" />

    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>
    <LoadingSkeleton v-if="store.loading && !store.dashboard" variant="card" />

    <template v-else-if="store.dashboard">
      <section class="grid grid-cols-1 gap-4 xs:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Total messages" :value="store.dashboard.total_messages ?? 0" accent="brand" />
        <StatCard label="SMS delivered" :value="store.dashboard.sms_delivered ?? 0" accent="green" />
        <StatCard label="Email delivered" :value="store.dashboard.email_delivered ?? 0" accent="brand" />
        <StatCard label="Failed" :value="store.dashboard.failed_messages ?? 0" accent="red" />
        <StatCard label="Pending queue" :value="store.dashboard.pending_queue ?? 0" accent="amber" />
        <StatCard label="Retry queue" :value="store.dashboard.retry_queue ?? 0" accent="amber" />
        <StatCard label="Sent today" :value="store.dashboard.notifications_sent_today ?? 0" accent="slate" />
        <StatCard label="In-app today" :value="store.dashboard.in_app_sent_today ?? 0" accent="slate" />
      </section>

      <section class="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <VCard title="Provider status">
          <EmptyState
            v-if="!store.dashboard.providers?.length"
            title="No providers configured"
            description="Providers are seeded on migration."
            icon="communications"
          />
          <ul v-else class="space-y-3">
            <li
              v-for="provider in store.dashboard.providers"
              :key="provider.uuid"
              class="flex flex-wrap items-center justify-between gap-2 rounded-input bg-surface-muted px-4 py-3"
            >
              <div>
                <p class="font-medium text-slate-800">{{ provider.name }}</p>
                <p class="text-xs capitalize text-slate-500">{{ provider.provider_type.replace(/_/g, " ") }}</p>
              </div>
              <span
                class="text-xs font-semibold capitalize"
                :class="provider.connection_status === 'connected' ? 'text-success-600' : 'text-warning-600'"
              >
                {{ provider.connection_status }}
              </span>
            </li>
          </ul>
          <VButton class="mt-4" variant="secondary" size="sm" @click="router.push('/communications/providers')">
            Manage providers
          </VButton>
        </VCard>

        <VCard title="Quick links">
          <div class="grid grid-cols-1 gap-2 sm:grid-cols-2">
            <VButton variant="secondary" @click="router.push('/communications/templates')">Templates</VButton>
            <VButton variant="secondary" @click="router.push('/communications/logs?channel=sms')">SMS logs</VButton>
            <VButton variant="secondary" @click="router.push('/communications/logs?channel=email')">Email logs</VButton>
            <VButton variant="secondary" @click="router.push('/notifications')">Notification center</VButton>
          </div>
        </VCard>
      </section>
    </template>
  </div>
</template>
