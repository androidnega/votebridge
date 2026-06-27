<script setup>
import { onMounted, onUnmounted } from "vue";
import { ConnectionStatusIndicator, StatCard } from "@/components/dashboard";
import { operationsNav } from "@/config/moduleNav";
import { LoadingSkeleton, ModuleNav, PageHeader, VAlert, VCard } from "@/components/ui";
import { useOperationsStore } from "@/stores/operations";

const store = useOperationsStore();

onMounted(() => {
  store.fetchCommunications().catch(() => {});
  store.connectRealtime();
});

onUnmounted(() => store.disconnectRealtime());
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="Communications"
      subtitle="SMS, email, and notification delivery operations."
      :breadcrumbs="[{ label: 'Overview', to: '/' }, { label: 'Operations', to: '/operations' }, { label: 'Communications' }]"
    >
      <template #actions>
        <ConnectionStatusIndicator :status="store.realtimeStatus" />
      </template>
    </PageHeader>

    <ModuleNav :items="operationsNav" />
    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>
    <LoadingSkeleton v-if="store.loading && !store.communications" variant="stats" :rows="4" />

    <template v-else-if="store.communications">
      <section class="grid grid-cols-1 gap-4 xs:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Pending queue" :value="store.communications.pending_queue ?? 0" accent="amber" />
        <StatCard label="Retry queue" :value="store.communications.retry_queue ?? 0" accent="amber" />
        <StatCard label="Failed" :value="store.communications.failed_messages ?? 0" accent="red" />
        <StatCard label="SMS delivered" :value="store.communications.sms_delivered ?? 0" accent="green" />
        <StatCard label="Email delivered" :value="store.communications.email_delivered ?? 0" accent="brand" />
        <StatCard label="Sent today" :value="store.communications.notifications_sent_today ?? 0" accent="slate" />
      </section>

      <VCard title="Provider status">
        <ul class="space-y-2">
          <li
            v-for="provider in store.communications.providers || []"
            :key="provider.uuid"
            class="flex justify-between rounded-input bg-surface-muted px-3 py-2 text-sm"
          >
            <span>{{ provider.name }}</span>
            <span class="capitalize">{{ provider.connection_status }}</span>
          </li>
        </ul>
      </VCard>
    </template>
  </div>
</template>
