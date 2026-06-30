<script setup>
import { onMounted } from "vue";
import { useRouter } from "vue-router";
import { DeliveryLogTable } from "@/components/communications";
import { EmptyState, LoadingSkeleton, StatCard } from "@/components/dashboard";
import { VAlert, VButton } from "@/components/ui";
import { useNotificationsStore } from "@/stores/notifications";

const router = useRouter();
const store = useNotificationsStore();

onMounted(async () => {
  await store.fetchDashboard().catch(() => {});
  store.deliveryFilters.status = "pending";
  await store.fetchDeliveries({ status: "pending" }).catch(() => {});
});

async function processQueue() {
  await store.processQueue();
  store.deliveryFilters.status = "pending";
  await store.fetchDeliveries({ status: "pending" }).catch(() => {});
}

async function loadRetry() {
  store.deliveryFilters.status = "retrying";
  await store.fetchDeliveries({ status: "retrying" }).catch(() => {});
}
</script>

<template>
  <div class="space-y-8">
    <div class="flex flex-wrap items-start justify-between gap-4">
      <div>
        <VButton variant="ghost" size="sm" class="mb-2" @click="router.push('/dashboard/communications')">
          ← Back
        </VButton>
        <h2 class="text-2xl font-bold text-slate-900">Queue monitor</h2>
        <p class="mt-1 text-sm text-slate-500">Pending and retrying message queues.</p>
      </div>
      <VButton :loading="store.actionLoading" @click="processQueue">
        Process queue
      </VButton>
    </div>

    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>

    <section v-if="store.dashboard" class="grid grid-cols-1 gap-4 sm:grid-cols-2">
      <StatCard label="Pending" :value="store.dashboard.pending_queue ?? 0" accent="amber" />
      <StatCard label="Retrying" :value="store.dashboard.retry_queue ?? 0" accent="red" />
    </section>

    <div class="flex gap-2">
      <VButton size="sm" variant="secondary" @click="store.deliveryFilters.status = 'pending'; store.fetchDeliveries({ status: 'pending' })">
        Pending
      </VButton>
      <VButton size="sm" variant="secondary" @click="loadRetry">
        Retry queue
      </VButton>
    </div>

    <LoadingSkeleton v-if="store.loading && !store.deliveries.length" variant="list" :rows="4" />

    <DeliveryLogTable
      v-else-if="store.deliveries.length"
      :items="store.deliveries"
      show-retry
      @retry="store.retryDelivery($event)"
    />

    <EmptyState
      v-else
      title="Queue empty"
      description="No pending or retrying messages."
      icon="✓"
    />
  </div>
</template>
