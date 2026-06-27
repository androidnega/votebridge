<script setup>
import { onMounted, watch } from "vue";
import { useRoute } from "vue-router";
import { DeliveryLogTable } from "@/components/communications";
import { communicationsNav } from "@/config/moduleNav";
import { EmptyState, LoadingSkeleton, ModuleNav, PageHeader, VAlert, VButton, VInput } from "@/components/ui";
import { useNotificationsStore } from "@/stores/notifications";

const route = useRoute();
const store = useNotificationsStore();

async function load() {
  store.deliveryFilters.channel = route.query.channel?.toString() || "";
  store.deliveryFilters.status = route.query.status?.toString() || "";
  await store.fetchDeliveries().catch(() => {});
}

onMounted(load);
watch(() => route.query, load);

async function handleSearch() {
  await store.fetchDeliveries({ search: store.deliveryFilters.search }).catch(() => {});
}

async function handleRetry(uuid) {
  await store.retryDelivery(uuid);
}
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="Delivery logs"
      subtitle="SMS, email, and in-app delivery history."
      :breadcrumbs="[
        { label: 'Overview', to: '/' },
        { label: 'Communications', to: '/communications' },
        { label: 'Delivery logs' },
      ]"
    />

    <ModuleNav :items="communicationsNav" aria-label="Communications navigation" />

    <form class="flex flex-col gap-3 sm:flex-row sm:items-end" @submit.prevent="handleSearch">
      <VInput
        v-model="store.deliveryFilters.search"
        label="Search"
        placeholder="Recipient, template, subject…"
        class="flex-1"
      />
      <VButton type="submit" variant="secondary">Search</VButton>
    </form>

    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>

    <LoadingSkeleton v-if="store.loading && !store.deliveries.length" variant="list" :rows="6" />

    <DeliveryLogTable
      v-else-if="store.deliveries.length"
      :rows="store.deliveries"
      :loading="store.actionLoading"
      @retry="handleRetry"
    />

    <EmptyState
      v-else
      title="No delivery logs"
      description="Messages sent through the platform will appear here."
      icon="communications"
    />
  </div>
</template>
