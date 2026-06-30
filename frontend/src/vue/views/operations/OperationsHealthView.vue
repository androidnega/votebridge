<script setup>
import { onMounted } from "vue";
import OpsHealthBadge from "@/components/operations/OpsHealthBadge.vue";
import { operationsNav } from "@/config/moduleNav";
import { LoadingSkeleton, ModuleNav, PageHeader, VAlert, VCard } from "@/components/ui";
import { useOperationsStore } from "@/stores/operations";

const store = useOperationsStore();

onMounted(() => {
  store.fetchHealth().catch(() => {});
});
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="System health"
      subtitle="Infrastructure and integration health probes."
      :breadcrumbs="[{ label: 'Dashboard', to: '/dashboard' }, { label: 'Operations', to: '/dashboard/operations' }, { label: 'System Health' }]"
    >
      <template #actions>
        <OpsHealthBadge v-if="store.health" :status="store.health.overall_status" />
      </template>
    </PageHeader>

    <ModuleNav :items="operationsNav" />
    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>
    <LoadingSkeleton v-if="store.loading && !store.health" variant="stats" :rows="6" />

    <section v-else-if="store.health" class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
      <VCard
        v-for="component in store.health.components"
        :key="component.name"
        :title="component.name.replace(/_/g, ' ')"
      >
        <div class="space-y-2 text-sm">
          <OpsHealthBadge :status="component.status" />
          <p v-if="component.response_time_ms != null" class="text-slate-600">
            Response: {{ component.response_time_ms }} ms
          </p>
          <p v-if="component.usage_percent != null" class="text-slate-600">Usage: {{ component.usage_percent }}%</p>
          <p v-if="component.details" class="text-slate-500">{{ component.details }}</p>
          <p class="text-xs text-slate-400">Checked {{ new Date(component.checked_at).toLocaleString() }}</p>
        </div>
      </VCard>
    </section>
  </div>
</template>
