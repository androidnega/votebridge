<script setup>
import { defineAsyncComponent, onMounted, onUnmounted } from "vue";
import { StatCard, ConnectionStatusIndicator } from "@/components/dashboard";
import { useReportsWorkspace } from "@/composables/useReportsWorkspace";
import { useToast } from "@/composables/useToast";
import { useAuthStore } from "@/stores/auth";
import {
  EmptyState,
  LoadingSkeleton,
  PageHeader,
  StatusBadge,
  VAlert,
  VButton,
  VCard,
  VTable,
} from "@/components/ui";

const LineChart = defineAsyncComponent(() => import("@/components/charts/LineChart.vue"));
const BarChart = defineAsyncComponent(() => import("@/components/charts/BarChart.vue"));
const PieChart = defineAsyncComponent(() => import("@/components/charts/PieChart.vue"));

const authStore = useAuthStore();
const toast = useToast();

const {
  store,
  filters,
  initialLoading,
  exportLoading,
  filterOptions,
  filteredElectionRows,
  kpis,
  turnoutTrendLabels,
  turnoutTrendValues,
  facultyChartLabels,
  facultyChartValues,
  electionDistribution,
  governanceSummary,
  loadWorkspace,
  resetFilters,
  exportReport,
} = useReportsWorkspace();

const tableColumns = [
  { key: "title", label: "Election" },
  { key: "status", label: "Status" },
  { key: "turnout_percent", label: "Turnout %" },
  { key: "eligible_voters", label: "Registered" },
  { key: "votes_cast", label: "Votes cast" },
];

const filterSelectClass =
  "w-full min-h-[44px] rounded-input border border-border bg-surface px-3 py-2 text-sm text-slate-700 focus:border-brand focus:outline-none focus:ring-2 focus:ring-brand/20";

async function handleExport(format) {
  try {
    await exportReport(format);
    toast.success(`${format.toUpperCase()} export ready.`);
  } catch {
    toast.error(store.error || "Export failed.");
  }
}

onMounted(() => {
  loadWorkspace();
  requestAnimationFrame(() => store.connectRealtime());
});

onUnmounted(() => store.disconnectRealtime());
</script>

<template>
  <div class="vb-page space-y-section">
    <PageHeader
      title="Election Reports"
      subtitle="Official institutional reporting and election analytics."
      :breadcrumbs="[{ label: 'Dashboard', to: '/dashboard' }, { label: 'Reports' }]"
    >
      <template #actions>
        <ConnectionStatusIndicator :status="store.realtimeStatus" />
      </template>
    </PageHeader>

    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>

    <LoadingSkeleton v-if="initialLoading && !store.overview" variant="stats" :rows="4" />

    <template v-else>
      <section class="grid grid-cols-1 gap-4 xs:grid-cols-2 lg:grid-cols-4">
        <StatCard
          label="Completed elections"
          :value="kpis.completedElections"
          accent="brand"
        />
        <StatCard
          label="Average turnout"
          :value="`${kpis.averageTurnout}%`"
          accent="green"
        />
        <StatCard
          label="Registered voters"
          :value="kpis.registeredVoters"
          accent="slate"
        />
        <StatCard
          label="Total votes cast"
          :value="kpis.totalVotesCast"
          accent="brand"
        />
      </section>

      <section
        v-if="authStore.isSuperAdmin && governanceSummary"
        class="grid grid-cols-2 gap-4 lg:grid-cols-4"
        aria-label="Governance summary"
      >
        <VCard padding="sm">
          <p class="text-xs font-medium uppercase tracking-wide text-slate-500">Security alerts</p>
          <p class="mt-1 text-2xl font-semibold text-slate-900">{{ governanceSummary.securityAlerts }}</p>
        </VCard>
        <VCard padding="sm">
          <p class="text-xs font-medium uppercase tracking-wide text-slate-500">Fraud cases</p>
          <p class="mt-1 text-2xl font-semibold text-slate-900">{{ governanceSummary.fraudCases }}</p>
        </VCard>
        <VCard padding="sm">
          <p class="text-xs font-medium uppercase tracking-wide text-slate-500">SMS delivery</p>
          <p class="mt-1 text-2xl font-semibold text-slate-900">{{ governanceSummary.smsSuccessPercent }}%</p>
        </VCard>
        <VCard padding="sm">
          <p class="text-xs font-medium uppercase tracking-wide text-slate-500">USSD requests today</p>
          <p class="mt-1 text-2xl font-semibold text-slate-900">{{ governanceSummary.ussdRequestsToday }}</p>
        </VCard>
      </section>

      <VCard title="Filters" subtitle="Refine charts and the election report table.">
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
          <label class="block text-sm text-slate-600">
            <span class="mb-1 block font-medium">Election</span>
            <select v-model="filters.election" :class="filterSelectClass">
              <option value="">All elections</option>
              <option v-for="option in filterOptions.elections" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </label>

          <label class="block text-sm text-slate-600">
            <span class="mb-1 block font-medium">Academic year</span>
            <select v-model="filters.academicYear" :class="filterSelectClass">
              <option value="">All years</option>
              <option v-for="year in filterOptions.academicYears" :key="year" :value="year">
                {{ year }}
              </option>
            </select>
          </label>

          <label class="block text-sm text-slate-600">
            <span class="mb-1 block font-medium">Faculty</span>
            <select v-model="filters.faculty" :class="filterSelectClass">
              <option value="">All faculties</option>
              <option v-for="faculty in filterOptions.faculties" :key="faculty" :value="faculty">
                {{ faculty }}
              </option>
            </select>
          </label>

          <label class="block text-sm text-slate-600">
            <span class="mb-1 block font-medium">Department</span>
            <select v-model="filters.department" :class="filterSelectClass">
              <option value="">All departments</option>
              <option v-for="department in filterOptions.departments" :key="department" :value="department">
                {{ department }}
              </option>
            </select>
          </label>

          <label class="block text-sm text-slate-600">
            <span class="mb-1 block font-medium">Programme</span>
            <select v-model="filters.programme" :class="filterSelectClass">
              <option value="">All programmes</option>
              <option
                v-for="programme in filterOptions.programmes"
                :key="programme.value"
                :value="programme.value"
              >
                {{ programme.label }}
              </option>
            </select>
          </label>
        </div>

        <div class="mt-4 flex justify-end">
          <VButton size="sm" variant="secondary" @click="resetFilters">Reset filters</VButton>
        </div>
      </VCard>

      <section class="grid grid-cols-1 gap-4 xl:grid-cols-3">
        <VCard title="Turnout trend" class="xl:col-span-2">
          <LineChart
            v-if="turnoutTrendLabels.length"
            :labels="turnoutTrendLabels"
            :series="[{ name: 'Votes', data: turnoutTrendValues, area: true }]"
          />
          <EmptyState
            v-else
            title="No trend data"
            description="Adjust filters or wait for completed elections."
            icon="analytics"
          />
        </VCard>

        <VCard title="Election distribution">
          <PieChart
            v-if="electionDistribution.length"
            :items="electionDistribution"
            donut
          />
          <EmptyState
            v-else
            title="No distribution data"
            description="No elections match the current filters."
            icon="analytics"
          />
        </VCard>
      </section>

      <VCard title="Faculty participation">
        <BarChart
          v-if="facultyChartLabels.length"
          :labels="facultyChartLabels"
          :values="facultyChartValues"
          horizontal
        />
        <EmptyState
          v-else
          title="No faculty data"
          description="Participation breakdown is unavailable for the selected filters."
          icon="chart"
        />
      </VCard>

      <VCard>
        <template #header>
          <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <h3 class="text-lg font-semibold text-ink-primary">Election reports</h3>
              <p class="mt-1 text-sm text-ink-secondary">Filtered institutional election data.</p>
            </div>
            <div class="flex flex-wrap gap-2">
              <VButton
                size="sm"
                variant="secondary"
                :loading="exportLoading"
                @click="handleExport('pdf')"
              >
                Export PDF
              </VButton>
              <VButton
                size="sm"
                variant="secondary"
                :loading="exportLoading"
                @click="handleExport('excel')"
              >
                Export Excel
              </VButton>
              <VButton
                size="sm"
                variant="primary"
                :loading="exportLoading"
                @click="handleExport('csv')"
              >
                Export CSV
              </VButton>
            </div>
          </div>
        </template>

        <VTable
          :columns="tableColumns"
          :rows="filteredElectionRows"
          empty-text="No elections match the selected filters."
        >
          <template #cell-status="{ row }">
            <StatusBadge :status="row.status" />
          </template>
          <template #cell-turnout_percent="{ row }">
            {{ row.turnout_percent ?? "—" }}%
          </template>
          <template #cell-votes_cast="{ row }">
            {{ row.votes_cast ?? "—" }}
          </template>
        </VTable>
      </VCard>
    </template>
  </div>
</template>
