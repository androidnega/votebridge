<script setup>
import { computed, onMounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { DeliveryLogTable } from "@/components/communications";
import {
  EmptyState,
  LoadingSkeleton,
  PageHeader,
  VAlert,
  VButton,
  VInput,
  VTable,
} from "@/components/ui";
import { useNotificationsStore } from "@/stores/notifications";
import { useOperationsStore } from "@/stores/operations";
import { useUssdStore } from "@/stores/ussd";

const route = useRoute();
const router = useRouter();
const operationsStore = useOperationsStore();
const notificationsStore = useNotificationsStore();
const ussdStore = useUssdStore();

const tabs = [
  { id: "operations", label: "Operations audit" },
  { id: "communications", label: "Communications" },
  { id: "ussd", label: "USSD" },
];

const activeTab = computed(() => {
  const tab = route.query.tab?.toString() || "operations";
  return tabs.some((item) => item.id === tab) ? tab : "operations";
});

const operationsColumns = [
  { key: "timestamp", label: "Time" },
  { key: "event_type", label: "Event" },
  { key: "category", label: "Category" },
  { key: "title", label: "Title" },
  { key: "user_email", label: "User" },
];

const ussdColumns = [
  { key: "carrier_session_id", label: "Session" },
  { key: "step_after", label: "Step" },
  { key: "outcome", label: "Outcome" },
  { key: "duration_ms", label: "Ms" },
  { key: "created_at", label: "Time" },
];

function setTab(tabId) {
  router.replace({ query: { ...route.query, tab: tabId } });
}

async function loadTab(tabId = activeTab.value) {
  if (tabId === "operations") {
    await operationsStore.fetchLogs().catch(() => {});
    return;
  }
  if (tabId === "communications") {
    await notificationsStore.fetchDeliveries().catch(() => {});
    return;
  }
  if (tabId === "ussd") {
    await ussdStore.fetchLogs().catch(() => {});
  }
}

function formatOperationsRows(rows) {
  return rows.map((row) => ({
    ...row,
    timestamp: row.timestamp ? new Date(row.timestamp).toLocaleString() : "—",
  }));
}

function formatUssdRows(rows) {
  return rows.map((row) => ({
    ...row,
    created_at: row.created_at ? new Date(row.created_at).toLocaleString() : "—",
  }));
}

const isLoading = computed(() => {
  if (activeTab.value === "operations") {
    return operationsStore.loading && !operationsStore.logs.items.length;
  }
  if (activeTab.value === "communications") {
    return notificationsStore.loading && !notificationsStore.deliveries.length;
  }
  return ussdStore.loading && !ussdStore.logs.length;
});

const tabError = computed(() => {
  if (activeTab.value === "operations") return operationsStore.error;
  if (activeTab.value === "communications") return notificationsStore.error;
  return ussdStore.error;
});

const isStrongroomAudit = computed(() => route.name === "strongroom-audit");
const pageTitle = computed(() => (isStrongroomAudit.value ? "Audit trail" : "Platform logs"));
const breadcrumbs = computed(() =>
  isStrongroomAudit.value
    ? [
        { label: "Strong room", to: "/dashboard/strongroom" },
        { label: "Investigations", to: "/dashboard/strongroom/investigations" },
        { label: "Audit trail" },
      ]
    : [{ label: "Dashboard", to: "/dashboard" }, { label: "Platform logs" }]
);

onMounted(() => loadTab());
watch(activeTab, (tab) => loadTab(tab));
</script>

<template>
  <div class="vb-page">
    <PageHeader
      :title="pageTitle"
      subtitle="Operations audit, communications delivery, and USSD activity in one place."
      :breadcrumbs="breadcrumbs"
    />

    <div
      class="flex flex-wrap gap-2 border-b border-border pb-4"
      role="tablist"
      aria-label="Log sources"
    >
      <VButton
        v-for="tab in tabs"
        :key="tab.id"
        size="sm"
        :variant="activeTab === tab.id ? 'primary' : 'secondary'"
        role="tab"
        :aria-selected="activeTab === tab.id"
        @click="setTab(tab.id)"
      >
        {{ tab.label }}
      </VButton>
    </div>

    <VAlert v-if="tabError" variant="error">{{ tabError }}</VAlert>

    <template v-if="activeTab === 'operations'">
      <form class="flex flex-col gap-3 sm:flex-row sm:items-end" @submit.prevent="loadTab('operations')">
        <VInput v-model="operationsStore.logsFilters.search" label="Search audit logs" class="flex-1" />
        <VButton type="submit" variant="secondary">Search</VButton>
      </form>

      <LoadingSkeleton v-if="isLoading" variant="list" :rows="8" />
      <VTable
        v-else-if="operationsStore.logs.items.length"
        :columns="operationsColumns"
        :rows="formatOperationsRows(operationsStore.logs.items)"
        empty-text="No log entries."
      />
      <EmptyState
        v-else
        title="No operations logs"
        description="Adjust filters or try another time range."
        icon="operations"
      />
    </template>

    <template v-else-if="activeTab === 'communications'">
      <form
        class="flex flex-col gap-3 sm:flex-row sm:items-end"
        @submit.prevent="notificationsStore.fetchDeliveries({ search: notificationsStore.deliveryFilters.search })"
      >
        <VInput
          v-model="notificationsStore.deliveryFilters.search"
          label="Search deliveries"
          placeholder="Recipient, template, subject…"
          class="flex-1"
        />
        <VButton type="submit" variant="secondary">Search</VButton>
      </form>

      <LoadingSkeleton v-if="isLoading" variant="list" :rows="6" />
      <DeliveryLogTable
        v-else-if="notificationsStore.deliveries.length"
        :rows="notificationsStore.deliveries"
        @retry="notificationsStore.retryDelivery"
      />
      <EmptyState
        v-else
        title="No delivery logs"
        description="SMS, email, and in-app deliveries will appear here."
        icon="communications"
      />
    </template>

    <template v-else>
      <form class="flex flex-col gap-3 sm:flex-row sm:items-end" @submit.prevent="loadTab('ussd')">
        <VInput v-model="ussdStore.logFilters.search" label="Search USSD logs" class="flex-1" />
        <VButton type="submit" variant="secondary">Search</VButton>
      </form>

      <div class="flex flex-wrap gap-2">
        <VButton
          size="sm"
          :variant="!ussdStore.logFilters.outcome ? 'primary' : 'secondary'"
          @click="ussdStore.logFilters.outcome = ''; loadTab('ussd')"
        >
          All
        </VButton>
        <VButton
          size="sm"
          :variant="ussdStore.logFilters.outcome === 'success' ? 'primary' : 'secondary'"
          @click="ussdStore.logFilters.outcome = 'success'; loadTab('ussd')"
        >
          Success
        </VButton>
        <VButton
          size="sm"
          :variant="ussdStore.logFilters.outcome === 'error' ? 'primary' : 'secondary'"
          @click="ussdStore.logFilters.outcome = 'error'; loadTab('ussd')"
        >
          Errors
        </VButton>
      </div>

      <LoadingSkeleton v-if="isLoading" variant="list" :rows="6" />
      <VTable
        v-else-if="ussdStore.logs.length"
        :columns="ussdColumns"
        :rows="formatUssdRows(ussdStore.logs)"
        empty-text="No USSD log entries."
      />
      <EmptyState
        v-else
        title="No USSD logs"
        description="USSD callback activity will appear here."
        icon="ussd"
      />
    </template>
  </div>
</template>
