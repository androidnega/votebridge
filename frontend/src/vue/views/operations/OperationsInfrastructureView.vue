<script setup>
import { onMounted } from "vue";
import InfrastructureDiagram from "@/components/operations/InfrastructureDiagram.vue";
import { operationsNav } from "@/config/moduleNav";
import { LoadingSkeleton, ModuleNav, PageHeader, VAlert } from "@/components/ui";
import { useOperationsStore } from "@/stores/operations";

const store = useOperationsStore();

onMounted(() => {
  store.fetchInfrastructure().catch(() => {});
});
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="Infrastructure"
      subtitle="Platform topology and service relationships."
      :breadcrumbs="[{ label: 'Dashboard', to: '/dashboard' }, { label: 'Operations', to: '/dashboard/operations' }, { label: 'Infrastructure' }]"
    />
    <ModuleNav :items="operationsNav" />
    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>
    <LoadingSkeleton v-if="store.loading && !store.infrastructure" variant="card" />
    <InfrastructureDiagram
      v-else-if="store.infrastructure"
      :nodes="store.infrastructure.nodes"
      :links="store.infrastructure.links"
    />
  </div>
</template>
