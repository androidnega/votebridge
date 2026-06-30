<script setup>
import { onMounted, onUnmounted } from "vue";
import { ActivityFeed, ConnectionStatusIndicator } from "@/components/dashboard";
import { operationsNav } from "@/config/moduleNav";
import { ModuleNav, PageHeader, VAlert, VButton, VInput } from "@/components/ui";
import { useOperationsStore } from "@/stores/operations";

const store = useOperationsStore();
const categories = [
  { id: "", label: "All" },
  { id: "users", label: "Users" },
  { id: "election", label: "Election" },
  { id: "security", label: "Security" },
  { id: "fraud", label: "Fraud" },
  { id: "strongroom", label: "Strongroom" },
  { id: "ussd", label: "USSD" },
  { id: "communications", label: "Communications" },
  { id: "system", label: "System" },
];

onMounted(() => {
  store.fetchActivity().catch(() => {});
  store.connectRealtime();
});

onUnmounted(() => store.disconnectRealtime());

function setCategory(id) {
  store.activityFilters.category = id;
  store.fetchActivity().catch(() => {});
}

function search() {
  store.fetchActivity().catch(() => {});
}

function loadMore() {
  store.loadMoreActivity().catch(() => {});
}
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="Live activity"
      subtitle="Unified operational event stream from audit and realtime feeds."
      :breadcrumbs="[{ label: 'Dashboard', to: '/dashboard' }, { label: 'Operations', to: '/dashboard/operations' }, { label: 'Live Activity' }]"
    >
      <template #actions>
        <ConnectionStatusIndicator :status="store.realtimeStatus" />
      </template>
    </PageHeader>

    <ModuleNav :items="operationsNav" />

    <form class="flex flex-col gap-3 sm:flex-row sm:items-end" @submit.prevent="search">
      <VInput v-model="store.activityFilters.search" label="Search" class="flex-1" placeholder="Search events…" />
      <VButton type="submit" variant="secondary">Search</VButton>
    </form>

    <div class="flex flex-wrap gap-2">
      <VButton
        v-for="cat in categories"
        :key="cat.id"
        size="sm"
        :variant="store.activityFilters.category === cat.id ? 'primary' : 'secondary'"
        @click="setCategory(cat.id)"
      >
        {{ cat.label }}
      </VButton>
    </div>

    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>

    <ActivityFeed
      :items="[...store.liveEvents, ...store.activity.items]"
      :loading="store.loading && !store.activity.items.length"
      empty-title="No activity recorded"
      empty-description="Operational events will appear as the platform is used."
    />

    <div v-if="store.activity.items.length < store.activity.total" class="flex justify-center">
      <VButton variant="secondary" :loading="store.loading" @click="loadMore">Load more</VButton>
    </div>
  </div>
</template>
