<script setup>
import { computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import SettingsTintedCard from "@/components/system-control/SettingsTintedCard.vue";
import SystemSectionCard from "@/components/system-control/SystemSectionCard.vue";
import { systemControlSections } from "@/config/systemControlHub";
import { settingsRoutes as r } from "@/config/settingsRoutes";
import { settingsNav } from "@/config/moduleNav";
import { useToast } from "@/composables/useToast";
import { LoadingSkeleton, ModuleNav, PageHeader, VAlert, VButton } from "@/components/ui";
import { useSystemControlStore } from "@/stores/systemControl";

const router = useRouter();
const store = useSystemControlStore();
const toast = useToast();

const overview = computed(() => store.overview);
const maintenanceEnabled = computed(() => Boolean(overview.value?.maintenance_status?.is_enabled));

function refresh() {
  store.fetchOverview().catch(() => toast.error("Could not refresh settings status."));
}

function openAction(to) {
  router.push(to);
}

onMounted(() => {
  store.fetchOverview().catch(() => {});
});
</script>

<template>
  <div class="vb-page space-y-section">
    <PageHeader
      title="Settings"
      subtitle="Platform governance control center — grouped by responsibility."
      :breadcrumbs="[{ label: 'Dashboard', to: '/dashboard' }, { label: 'Settings' }]"
    >
      <template #actions>
        <VButton variant="secondary" size="sm" :loading="store.loading" @click="refresh">
          Refresh
        </VButton>
      </template>
    </PageHeader>

    <ModuleNav :items="settingsNav" aria-label="Settings navigation" />

    <VAlert v-if="store.error" variant="error" dismissible @dismiss="store.clearError()">
      {{ store.error }}
    </VAlert>

    <VAlert
      v-if="maintenanceEnabled"
      variant="warning"
      title="Maintenance mode is active"
      class="border-warning-200"
    >
      <p>{{ overview?.maintenance_status?.message || "Users may be unable to access the platform." }}</p>
      <VButton
        variant="secondary"
        size="sm"
        class="mt-3"
        @click="openAction(r.operations.maintenance)"
      >
        Manage maintenance
      </VButton>
    </VAlert>

    <LoadingSkeleton v-if="store.loading && !overview" variant="stats" :rows="6" />

    <section v-else aria-label="Settings groups">
      <div class="grid grid-cols-1 gap-5 md:grid-cols-2 xl:grid-cols-3">
        <SystemSectionCard
          v-for="section in systemControlSections"
          :key="section.id"
          :section-id="section.id"
          :title="section.title"
          :description="section.description"
          :icon="section.icon"
          :hub-to="section.hubTo"
          :items="section.items"
        />
      </div>
    </section>
  </div>
</template>
