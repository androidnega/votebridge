<script setup>
import { onMounted } from "vue";
import OpsHealthBadge from "@/components/operations/OpsHealthBadge.vue";
import { StatCard } from "@/components/dashboard";
import { operationsNav } from "@/config/moduleNav";
import { LoadingSkeleton, ModuleNav, PageHeader, VAlert, VCard } from "@/components/ui";
import { useOperationsStore } from "@/stores/operations";

const store = useOperationsStore();

onMounted(() => {
  store.fetchQueues().catch(() => {});
});
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="Queues"
      subtitle="Notification, SMS, email, and USSD queue status."
      :breadcrumbs="[{ label: 'Dashboard', to: '/dashboard' }, { label: 'Operations', to: '/dashboard/operations' }, { label: 'Queues' }]"
    />
    <ModuleNav :items="operationsNav" />
    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>
    <LoadingSkeleton v-if="store.loading && !store.queues" variant="stats" :rows="4" />

    <template v-else-if="store.queues">
      <section class="grid grid-cols-1 gap-4 xs:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Pending notifications" :value="store.queues.notification_queue?.pending ?? 0" accent="amber" />
        <StatCard label="Retry notifications" :value="store.queues.notification_queue?.retry ?? 0" accent="amber" />
        <StatCard label="Failed deliveries" :value="store.queues.notification_queue?.failed ?? 0" accent="red" />
        <StatCard label="USSD active" :value="store.queues.ussd_queue?.active ?? 0" accent="brand" />
      </section>

      <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <VCard title="Worker status">
          <p class="text-sm text-slate-600">{{ store.queues.worker_status?.details }}</p>
          <OpsHealthBadge
            v-if="store.queues.worker_status"
            :status="store.queues.worker_status.status"
            class="mt-3 inline-flex"
          />
        </VCard>
        <VCard title="USSD queue">
          <dl class="grid grid-cols-2 gap-3 text-sm">
            <div><dt class="text-slate-500">Completed</dt><dd>{{ store.queues.ussd_queue?.completed ?? 0 }}</dd></div>
            <div><dt class="text-slate-500">Failed</dt><dd>{{ store.queues.ussd_queue?.failed ?? 0 }}</dd></div>
          </dl>
        </VCard>
      </div>
    </template>
  </div>
</template>
