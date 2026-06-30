<script setup>
import { computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import SystemHealthTile from "@/components/system-control/SystemHealthTile.vue";
import SystemSectionCard from "@/components/system-control/SystemSectionCard.vue";
import OpsHealthBadge from "@/components/operations/OpsHealthBadge.vue";
import {
  infrastructureServices,
  normalizeHealthStatus,
  quickActionRoutes,
  systemControlSections,
  systemStatusLabel,
} from "@/config/systemControlHub";
import { settingsNav } from "@/config/moduleNav";
import { useToast } from "@/composables/useToast";
import { EmptyState, LoadingSkeleton, ModuleNav, PageHeader, SectionHeader, VAlert, VButton, VCard, VIcon } from "@/components/ui";
import { useSystemControlStore } from "@/stores/systemControl";

const router = useRouter();
const store = useSystemControlStore();
const toast = useToast();

const overview = computed(() => store.overview);

const systemStatus = computed(() => normalizeHealthStatus(overview.value?.system_status));
const statusHeadline = computed(() => systemStatusLabel(overview.value?.system_status));

const maintenanceEnabled = computed(() => Boolean(overview.value?.maintenance_status?.is_enabled));

const platformState = computed(() => overview.value?.platform_state || {});

const statusBannerClass = computed(() => {
  const styles = {
    healthy: "border-success-200 bg-success-50",
    warning: "border-warning-200 bg-warning-50",
    critical: "border-danger-200 bg-danger-50",
    unknown: "border-border bg-white",
  };
  return styles[systemStatus.value] || styles.unknown;
});

const statusDotClass = computed(() => {
  const styles = {
    healthy: "bg-success-600",
    warning: "bg-warning-600",
    critical: "bg-danger-600",
    unknown: "bg-slate-400",
  };
  return styles[systemStatus.value] || styles.unknown;
});

const platformFacts = computed(() => {
  if (!overview.value) return [];
  return [
    { label: "Environment", value: overview.value.environment },
    { label: "Version", value: overview.value.application_version },
    { label: "Institution", value: overview.value.institution },
    {
      label: "Current platform state",
      value: platformState.value.primary || "Unknown",
      detail: platformState.value.secondary,
    },
  ];
});

const adminActivity = computed(() => overview.value?.admin_activity || []);

const quickActions = computed(() => {
  const actions = overview.value?.quick_actions || [];
  return actions.map((action) => ({
    ...action,
    to: quickActionRoutes[action.action] || "/dashboard/settings",
  }));
});

const lastBackupLabel = computed(() => {
  if (!overview.value?.last_backup) return "No backups recorded";
  return new Date(overview.value.last_backup).toLocaleString();
});

function refresh() {
  store.fetchOverview().catch(() => toast.error("Could not refresh system status."));
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
      subtitle="Platform governance, infrastructure, integrations, and administration."
      :breadcrumbs="[{ label: 'Dashboard', to: '/dashboard' }, { label: 'Settings' }]"
    >
      <template #actions>
        <VButton variant="secondary" size="sm" :loading="store.loading" @click="refresh">
          Refresh status
        </VButton>
      </template>
    </PageHeader>

    <ModuleNav :items="settingsNav" aria-label="Settings navigation" />

    <VAlert v-if="store.error" variant="error" dismissible @dismiss="store.clearError()">
      {{ store.error }}
    </VAlert>

    <LoadingSkeleton v-if="store.loading && !overview" variant="stats" :rows="8" />

    <template v-else-if="overview">
      <VAlert
        v-if="maintenanceEnabled"
        variant="warning"
        title="Maintenance mode is active"
        class="border-warning-200"
      >
        <p>{{ overview.maintenance_status?.message || "Users may be unable to access the platform." }}</p>
        <VButton
          variant="secondary"
          size="sm"
          class="mt-3"
          @click="openAction('/dashboard/settings/maintenance')"
        >
          Manage maintenance
        </VButton>
      </VAlert>

      <section
        class="rounded-card border p-card shadow-card"
        :class="statusBannerClass"
        aria-label="Platform status"
      >
        <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div class="flex items-start gap-3">
            <span
              class="mt-1.5 h-3 w-3 shrink-0 rounded-full"
              :class="statusDotClass"
              aria-hidden="true"
            />
            <div>
              <p class="text-xs font-semibold uppercase tracking-wide text-slate-500">Platform status</p>
              <h2 class="mt-1 text-xl font-semibold text-slate-900">{{ statusHeadline }}</h2>
              <p class="mt-1 text-sm text-slate-600">
                Release {{ overview.release_channel || "stable" }}
                <span v-if="overview.build_number"> · Build {{ overview.build_number }}</span>
              </p>
            </div>
          </div>
          <div class="flex flex-wrap gap-2">
            <span
              v-for="fact in platformFacts"
              :key="fact.label"
              class="inline-flex max-w-full flex-col rounded-input border border-white/60 bg-white/80 px-3 py-2 text-left shadow-sm backdrop-blur-sm"
            >
              <span class="text-[0.6875rem] font-semibold uppercase tracking-wide text-slate-500">
                {{ fact.label }}
              </span>
              <span class="mt-0.5 truncate text-sm font-medium text-slate-800">{{ fact.value }}</span>
              <span v-if="fact.detail" class="mt-0.5 text-xs text-slate-500">{{ fact.detail }}</span>
            </span>
          </div>
        </div>
      </section>

      <div class="grid grid-cols-1 gap-4 xl:grid-cols-3">
        <div class="space-y-4 xl:col-span-2">
          <VCard title="Infrastructure health" subtitle="Core services and integrations">
            <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
              <SystemHealthTile
                v-for="service in infrastructureServices"
                :key="service.key"
                :label="service.label"
                :icon="service.icon"
                :status="overview[service.key]"
              />
            </div>
          </VCard>

          <div>
            <SectionHeader
              title="Configuration areas"
              subtitle="Platform governance grouped by responsibility."
            />
            <div class="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-2">
              <SystemSectionCard
                v-for="section in systemControlSections"
                :key="section.id"
                :title="section.title"
                :description="section.description"
                :icon="section.icon"
                :items="section.items"
              />
            </div>
          </div>
        </div>

        <aside class="space-y-4">
          <VCard title="Quick actions" subtitle="Common platform administration tasks">
            <ul class="space-y-2">
              <li v-for="action in quickActions" :key="action.action">
                <button
                  type="button"
                  class="flex w-full min-h-touch items-center justify-between gap-3 rounded-input border border-border px-4 py-3 text-left transition-colors hover:border-brand-200 hover:bg-brand-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-600"
                  @click="openAction(action.to)"
                >
                  <span>
                    <span class="block text-sm font-medium text-slate-800">{{ action.label }}</span>
                    <span v-if="action.requires_step_up" class="mt-0.5 block text-xs text-slate-500">
                      Step-up verification required on save
                    </span>
                  </span>
                  <VIcon name="chevronRight" size="sm" class="shrink-0 text-slate-400" />
                </button>
              </li>
            </ul>
          </VCard>

          <VCard title="Administrative activity" subtitle="Recent platform administration events">
            <ul v-if="adminActivity.length" class="divide-y divide-border">
              <li v-for="item in adminActivity" :key="item.id" class="py-3">
                <p class="text-sm font-medium text-slate-800">{{ item.title }}</p>
                <p class="mt-0.5 text-xs text-slate-500">
                  <span v-if="item.actor">{{ item.actor }} · </span>
                  {{ item.timestamp ? new Date(item.timestamp).toLocaleString() : "" }}
                </p>
              </li>
            </ul>
            <EmptyState
              v-else
              title="No recent activity"
              description="Backup, maintenance, and integration events appear here."
            />
            <VButton
              variant="secondary"
              size="sm"
              class="mt-4"
              @click="openAction('/dashboard/platform/logs')"
            >
              Export system audit
            </VButton>
          </VCard>

          <VCard title="Maintenance & backups">
            <div class="space-y-4">
              <div>
                <p class="text-xs font-semibold uppercase tracking-wide text-slate-500">Maintenance</p>
                <p class="mt-1 text-sm text-slate-700">
                  {{ overview.maintenance_status?.message || "No maintenance message configured." }}
                </p>
                <OpsHealthBadge
                  class="mt-2 inline-flex"
                  :status="maintenanceEnabled ? 'warning' : 'healthy'"
                />
              </div>
              <div class="border-t border-border pt-4">
                <p class="text-xs font-semibold uppercase tracking-wide text-slate-500">Last backup</p>
                <p class="mt-1 text-sm text-slate-700">{{ lastBackupLabel }}</p>
                <VButton
                  variant="secondary"
                  size="sm"
                  class="mt-3"
                  @click="openAction('/dashboard/settings/backup')"
                >
                  Open backup center
                </VButton>
              </div>
            </div>
          </VCard>

          <VCard title="Operations center">
            <p class="text-sm text-slate-600">
              Live queues, sessions, and infrastructure monitoring — separate from platform configuration.
            </p>
            <VButton variant="primary" size="sm" class="mt-4" @click="openAction('/dashboard/operations')">
              Open operations center
            </VButton>
          </VCard>
        </aside>
      </div>
    </template>
  </div>
</template>
