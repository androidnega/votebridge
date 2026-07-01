<script setup>
import { computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { GovernanceActivityFeed } from "@/components/governance";
import SettingsTintedCard from "@/components/system-control/SettingsTintedCard.vue";
import SystemHealthTile from "@/components/system-control/SystemHealthTile.vue";
import SystemSectionCard from "@/components/system-control/SystemSectionCard.vue";
import OpsHealthBadge from "@/components/operations/OpsHealthBadge.vue";
import {
  getSettingsQuickActionPalette,
  getSettingsSectionPalette,
  infrastructureServices,
  normalizeHealthStatus,
  quickActionRoutes,
  systemControlSections,
  systemStatusLabel,
} from "@/config/systemControlHub";
import { settingsRoutes as r } from "@/config/settingsRoutes";
import { settingsNav } from "@/config/moduleNav";
import { useToast } from "@/composables/useToast";
import { EmptyState, LoadingSkeleton, ModuleNav, PageHeader, SectionHeader, VAlert, VButton } from "@/components/ui";
import { useSystemControlStore } from "@/stores/systemControl";

const router = useRouter();
const store = useSystemControlStore();
const toast = useToast();

const overview = computed(() => store.overview);

const systemStatus = computed(() => normalizeHealthStatus(overview.value?.system_status));
const statusHeadline = computed(() => systemStatusLabel(overview.value?.system_status));

const maintenanceEnabled = computed(() => Boolean(overview.value?.maintenance_status?.is_enabled));

const platformState = computed(() => overview.value?.platform_state || {});

const statusBorderClass = computed(() => {
  const styles = {
    healthy: "border-l-success-600",
    warning: "border-l-warning-600",
    critical: "border-l-danger-600",
    unknown: "border-l-slate-300",
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

const activityFeedItems = computed(() =>
  adminActivity.value.map((item) => ({
    id: item.id,
    title: item.title,
    meta: [
      item.actor,
      item.timestamp ? new Date(item.timestamp).toLocaleString() : null,
    ]
      .filter(Boolean)
      .join(" · "),
  }))
);

const quickActions = computed(() => {
  const actions = overview.value?.quick_actions || [];
  return actions.map((action) => ({
    ...action,
    to: quickActionRoutes[action.action] || r.overview,
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

function factStyle(index) {
  const keys = ["platform-defaults", "about", "institution", "integrations"];
  const palette = getSettingsSectionPalette(keys[index % keys.length]);
  return {
    backgroundColor: palette.bg,
    borderColor: palette.border,
    color: palette.accent,
  };
}

function quickActionStyle(action) {
  const palette = getSettingsQuickActionPalette(action.action);
  return {
    "--tile-bg": palette.bg,
    "--tile-border": palette.border,
    "--tile-hover-bg": palette.hoverBg,
    "--tile-hover-border": palette.border,
  };
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
          @click="openAction(r.advanced.maintenance)"
        >
          Manage maintenance
        </VButton>
      </VAlert>

      <!-- Platform overview -->
      <section
        class="grid grid-cols-1 gap-4 lg:grid-cols-12"
        aria-label="Platform status"
      >
        <div
          class="overflow-hidden rounded-card border border-border bg-white shadow-card lg:col-span-5"
        >
          <div class="border-l-4 p-card" :class="statusBorderClass">
            <div class="flex items-start gap-3">
              <span
                class="mt-1.5 h-3 w-3 shrink-0 rounded-full"
                :class="statusDotClass"
                aria-hidden="true"
              />
              <div class="min-w-0">
                <p class="text-xs font-semibold uppercase tracking-wide text-slate-500">Platform status</p>
                <h2 class="mt-1 text-xl font-semibold text-slate-900">{{ statusHeadline }}</h2>
                <p class="mt-1 text-sm text-slate-600">
                  Release {{ overview.release_channel || "stable" }}
                  <span v-if="overview.build_number"> · Build {{ overview.build_number }}</span>
                </p>
              </div>
            </div>
          </div>
        </div>

        <dl class="grid grid-cols-2 gap-3 sm:grid-cols-4 lg:col-span-7">
          <div
            v-for="(fact, index) in platformFacts"
            :key="fact.label"
            class="min-w-0 rounded-input border px-3 py-2.5 shadow-card"
            :style="{
              backgroundColor: factStyle(index).backgroundColor,
              borderColor: factStyle(index).borderColor,
            }"
          >
            <dt
              class="text-[0.6875rem] font-semibold uppercase tracking-wide"
              :style="{ color: factStyle(index).color }"
            >
              {{ fact.label }}
            </dt>
            <dd class="mt-0.5 truncate text-sm font-medium text-slate-800" :title="String(fact.value)">
              {{ fact.value }}
            </dd>
            <dd v-if="fact.detail" class="mt-0.5 truncate text-xs text-slate-500" :title="fact.detail">
              {{ fact.detail }}
            </dd>
          </div>
        </dl>
      </section>

      <!-- Infrastructure -->
      <section aria-label="Infrastructure health">
        <SectionHeader title="Infrastructure health" subtitle="Core services and integrations" />
        <div class="mt-4 grid grid-cols-2 gap-3 md:grid-cols-3 xl:grid-cols-6">
          <SystemHealthTile
            v-for="service in infrastructureServices"
            :key="service.key"
            compact
            :label="service.label"
            :icon="service.icon"
            :status="overview[service.key]"
          />
        </div>
      </section>

      <!-- Configuration + sidebar -->
      <div class="grid grid-cols-1 gap-6 xl:grid-cols-12 xl:items-start">
        <div class="space-y-4 xl:col-span-8">
          <SectionHeader
            title="Configuration areas"
            subtitle="Platform governance grouped by responsibility."
          />
          <div class="grid grid-cols-1 gap-4 md:grid-cols-2 2xl:grid-cols-3">
            <SystemSectionCard
              v-for="section in systemControlSections"
              :key="section.id"
              :section-id="section.id"
              :title="section.title"
              :description="section.description"
              :icon="section.icon"
              :items="section.items"
            />
          </div>
        </div>

        <aside class="space-y-4 xl:col-span-4 xl:sticky xl:top-24">
          <SettingsTintedCard
            title="Quick actions"
            subtitle="Common platform administration tasks"
            palette-key="quick-actions"
          >
            <ul class="flex flex-wrap gap-2">
              <li v-for="action in quickActions" :key="action.action" class="max-w-full">
                <button
                  type="button"
                  class="settings-quick-action inline-flex min-h-touch max-w-full flex-col items-start rounded-input border px-3 py-2.5 text-left transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-600"
                  :style="quickActionStyle(action)"
                  @click="openAction(action.to)"
                >
                  <span class="whitespace-nowrap text-sm font-medium text-slate-800">{{ action.label }}</span>
                  <span v-if="action.requires_step_up" class="mt-0.5 whitespace-normal text-xs text-slate-600">
                    Step-up verification required on save
                  </span>
                </button>
              </li>
            </ul>
          </SettingsTintedCard>

          <SettingsTintedCard title="Maintenance & backups" palette-key="maintenance">
            <div class="space-y-4">
              <div>
                <p class="text-xs font-semibold uppercase tracking-wide text-slate-600">Maintenance</p>
                <p class="mt-1 text-sm text-slate-800">
                  {{ overview.maintenance_status?.message || "No maintenance message configured." }}
                </p>
                <OpsHealthBadge
                  class="mt-2 inline-flex"
                  :status="maintenanceEnabled ? 'warning' : 'healthy'"
                />
              </div>
              <div class="border-t pt-4" :style="{ borderColor: getSettingsSectionPalette('maintenance').border }">
                <p class="text-xs font-semibold uppercase tracking-wide text-slate-600">Last backup</p>
                <p class="mt-1 text-sm text-slate-800">{{ lastBackupLabel }}</p>
                <VButton
                  variant="secondary"
                  size="sm"
                  class="mt-3"
                  @click="openAction(r.advanced.backup)"
                >
                  Open backup center
                </VButton>
              </div>
            </div>
          </SettingsTintedCard>

          <SettingsTintedCard title="Operations center" palette-key="operations">
            <p class="text-sm text-slate-700">
              Live queues, sessions, and infrastructure monitoring — separate from platform configuration.
            </p>
            <VButton variant="primary" size="sm" class="mt-4" @click="openAction('/dashboard/operations')">
              Open operations center
            </VButton>
          </SettingsTintedCard>
        </aside>
      </div>

      <!-- Administrative activity -->
      <SettingsTintedCard
        title="Administrative activity"
        subtitle="Recent platform administration events"
        palette-key="activity"
      >
        <GovernanceActivityFeed v-if="activityFeedItems.length" :items="activityFeedItems" />
        <EmptyState
          v-else
          title="No recent activity"
          description="Backup, maintenance, and integration events appear here."
        />
        <template #footer>
          <VButton
            variant="secondary"
            size="sm"
            @click="openAction('/dashboard/platform/logs')"
          >
            Export system audit
          </VButton>
        </template>
      </SettingsTintedCard>
    </template>
  </div>
</template>

<style scoped>
.settings-quick-action {
  background-color: var(--tile-bg);
  border-color: var(--tile-border);
}

.settings-quick-action:hover {
  background-color: var(--tile-hover-bg);
  border-color: var(--tile-hover-border);
}
</style>
