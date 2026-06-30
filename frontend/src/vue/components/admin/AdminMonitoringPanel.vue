<script setup>
import { AdminKpiCard } from "@/components/admin";
import { GovernanceSectionCard } from "@/components/governance";
import { EmptyState } from "@/components/ui";
import { useAdminMonitoring } from "@/composables/useAdminMonitoring";

const { metrics, primaryElectionTitle, isLive, hasMonitoring } = useAdminMonitoring();
</script>

<template>
  <GovernanceSectionCard
    title="Election monitoring"
    :subtitle="
      primaryElectionTitle
        ? `Live operational metrics for ${primaryElectionTitle}`
        : 'Operational metrics for active elections'
    "
  >
    <div class="mb-5 flex flex-wrap items-center gap-2">
      <span
        v-if="isLive"
        class="inline-flex items-center gap-1.5 rounded-input border border-success-600/20 bg-success-600/10 px-2.5 py-1 text-[0.6875rem] font-semibold uppercase tracking-wide text-success-700"
      >
        <span class="h-1.5 w-1.5 animate-pulse rounded-full bg-success-600" aria-hidden="true" />
        Live updates
      </span>
      <span class="text-xs text-slate-500">
        Aggregate turnout and channel counts only — no candidate rankings while voting is open.
      </span>
    </div>

    <div v-if="hasMonitoring" class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-5">
      <AdminKpiCard
        v-for="metric in metrics"
        :key="metric.id"
        :id="metric.id"
        :title="metric.label"
        :value="metric.value"
        :detail="metric.detail"
        :health-status="metric.healthStatus"
      />
    </div>

    <EmptyState
      v-else
      icon="operations"
      title="Monitoring data unavailable"
      description="Refresh the dashboard once an election is open to load live monitoring metrics."
    />
  </GovernanceSectionCard>
</template>
