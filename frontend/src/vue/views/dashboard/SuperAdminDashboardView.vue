<script setup>
import { defineAsyncComponent, onMounted } from "vue";
import { useRouter } from "vue-router";
import { ConnectionStatusIndicator, LoadingSkeleton } from "@/components/dashboard";
import OpsHealthBadge from "@/components/operations/OpsHealthBadge.vue";
import { VAlert, VCard } from "@/components/ui";
import { useSuperAdminDashboard } from "@/composables/useSuperAdminDashboard";

const LineChart = defineAsyncComponent(() => import("@/components/charts/LineChart.vue"));
const BubbleChart = defineAsyncComponent(() => import("@/components/charts/BubbleChart.vue"));
const DonutChart = defineAsyncComponent(() => import("@/components/charts/DonutChart.vue"));
const BarChart = defineAsyncComponent(() => import("@/components/charts/BarChart.vue"));

const router = useRouter();
const {
  loading,
  error,
  greeting,
  todayLabel,
  platformHealth,
  openElections,
  kpis,
  participationLabels,
  participationSeries,
  authActivityLabels,
  authActivityBubbles,
  electionStatusItems,
  votingChannelLabels,
  operationalCards,
  realtime,
  loadDashboard,
} = useSuperAdminDashboard();

onMounted(() => {
  loadDashboard().catch(() => {});
});
</script>

<template>
  <div class="vb-page">
    <header class="flex flex-wrap items-start justify-between gap-4">
      <div class="min-w-0">
        <h2 class="text-2xl font-semibold text-slate-900">{{ greeting }}</h2>
        <p class="mt-1 text-sm text-slate-500">{{ todayLabel }} · Executive command center</p>
      </div>
      <ConnectionStatusIndicator
        v-if="realtime.isLive.value"
        :status="realtime.status.value"
        :label="realtime.label.value"
      />
    </header>

    <VAlert v-if="error" variant="error">{{ error }}</VAlert>
    <LoadingSkeleton v-if="loading" variant="stats" :rows="4" />

    <template v-else>
      <section
        class="flex flex-wrap items-center gap-4 rounded-card border border-border bg-white px-5 py-4 shadow-card"
        aria-label="Platform status"
      >
        <div class="flex items-center gap-2">
          <span class="text-sm text-slate-500">Platform health</span>
          <OpsHealthBadge :status="platformHealth" />
        </div>
        <div class="hidden h-4 w-px bg-border sm:block" aria-hidden="true" />
        <div class="text-sm text-slate-600">
          <span class="font-semibold text-slate-900">{{ openElections }}</span>
          open election{{ openElections === 1 ? "" : "s" }}
        </div>
        <div class="hidden h-4 w-px bg-border md:block" aria-hidden="true" />
        <div class="text-sm text-slate-600">
          Realtime
          <span class="font-medium capitalize text-slate-900">{{ realtime.status.value }}</span>
        </div>
      </section>

      <section class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <article
          v-for="kpi in kpis"
          :key="kpi.id"
          class="vb-kpi-card"
        >
          <p class="text-sm text-ink-secondary">{{ kpi.label }}</p>
          <p class="mt-2 text-3xl font-semibold tabular-nums tracking-tight text-ink-primary">
            {{ kpi.value }}
          </p>
          <p v-if="kpi.hint" class="mt-2 text-xs text-ink-secondary">{{ kpi.hint }}</p>
        </article>
      </section>

      <section class="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <VCard title="Participation trend" subtitle="Vote throughput — last 24 hours">
          <LineChart
            :labels="participationLabels"
            :series="participationSeries"
            height="280px"
          />
        </VCard>

        <VCard title="Authentication activity" subtitle="Sign-in volume by hour — bubble size = intensity">
          <BubbleChart
            v-if="authActivityBubbles.length"
            :labels="authActivityLabels"
            :points="authActivityBubbles"
            height="280px"
          />
          <p v-else class="py-12 text-center text-sm text-slate-500">No authentication activity yet.</p>
        </VCard>
      </section>

      <section class="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <VCard title="Election status" subtitle="Distribution across lifecycle">
          <DonutChart
            v-if="electionStatusItems.length"
            :items="electionStatusItems"
            donut
            height="280px"
          />
          <p v-else class="py-12 text-center text-sm text-slate-500">No elections recorded yet.</p>
        </VCard>

        <VCard title="Voting channels" subtitle="Votes cast by channel">
          <BarChart
            v-if="votingChannelLabels.values.length"
            :labels="votingChannelLabels.labels"
            :values="votingChannelLabels.values"
            horizontal
            height="280px"
          />
          <p v-else class="py-12 text-center text-sm text-slate-500">No voting activity yet.</p>
        </VCard>
      </section>

      <section class="grid grid-cols-1 gap-4 md:grid-cols-3">
        <VCard
          v-for="card in operationalCards"
          :key="card.id"
          :title="card.title"
          padding="sm"
          hoverable
          class="cursor-pointer"
          @click="router.push(card.route)"
        >
          <dl class="space-y-3">
            <div
              v-for="metric in card.metrics"
              :key="metric.label"
              class="flex items-baseline justify-between gap-3 text-sm"
            >
              <dt class="text-slate-500">{{ metric.label }}</dt>
              <dd class="font-semibold tabular-nums text-slate-900">{{ metric.value }}</dd>
            </div>
          </dl>
        </VCard>
      </section>
    </template>
  </div>
</template>
