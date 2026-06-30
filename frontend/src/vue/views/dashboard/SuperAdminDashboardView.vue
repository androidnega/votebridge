<script setup>
import { onMounted } from "vue";
import { useRouter } from "vue-router";
import { ConnectionStatusIndicator, LoadingSkeleton } from "@/components/dashboard";
import { GovernanceSummaryCard } from "@/components/governance";
import OpsHealthBadge from "@/components/operations/OpsHealthBadge.vue";
import { VAlert, VButton, VCard } from "@/components/ui";
import { useGovernanceDashboard } from "@/composables/useGovernanceDashboard";

const router = useRouter();
const {
  loading,
  error,
  greeting,
  todayLabel,
  platformHealth,
  governanceCards,
  securityPreviews,
  recentActivity,
  realtime,
  loadDashboard,
} = useGovernanceDashboard();

onMounted(() => {
  loadDashboard().catch(() => {});
});
</script>

<template>
  <div class="vb-page space-y-section">
    <header class="flex flex-wrap items-start justify-between gap-4">
      <div class="min-w-0">
        <h2 class="text-2xl font-semibold text-slate-900">{{ greeting }}</h2>
        <p class="mt-1 text-sm text-slate-500">{{ todayLabel }} · Governance overview</p>
      </div>
      <ConnectionStatusIndicator
        v-if="realtime.isLive.value"
        :status="realtime.status.value"
        :label="realtime.label.value"
      />
    </header>

    <VAlert v-if="error" variant="error">{{ error }}</VAlert>

    <section
      class="flex flex-wrap items-center gap-4 rounded-card border border-border bg-white px-5 py-4 shadow-card"
      aria-label="Platform status"
    >
      <div class="flex items-center gap-2">
        <span class="text-sm text-slate-500">Platform health</span>
        <OpsHealthBadge :status="platformHealth" />
      </div>
    </section>

    <LoadingSkeleton v-if="loading" variant="stats" :rows="8" />

    <template v-else>
      <section class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <GovernanceSummaryCard
          v-for="card in governanceCards"
          :key="card.id"
          :title="card.title"
          :count="card.count"
          :description="card.description"
          :action-label="card.actionLabel"
          @view="router.push(card.route)"
        />
      </section>

      <section class="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <VCard title="Security preview" subtitle="Lightweight governance signals — summaries only">
          <ul class="space-y-3">
            <li
              v-for="preview in securityPreviews"
              :key="preview.id"
              class="flex items-center justify-between gap-3 rounded-input border border-border px-4 py-3"
            >
              <div>
                <p class="text-sm font-medium text-ink-primary">{{ preview.title }}</p>
                <p class="text-xs text-ink-secondary">{{ preview.value }}</p>
              </div>
              <VButton size="sm" variant="ghost" @click="router.push(preview.route)">View</VButton>
            </li>
          </ul>
        </VCard>

        <VCard title="Recent platform activity" subtitle="Latest governance events">
          <ul v-if="recentActivity.length" class="divide-y divide-border">
            <li v-for="item in recentActivity" :key="item.id" class="py-3">
              <p class="text-sm font-medium text-ink-primary">{{ item.title }}</p>
              <p v-if="item.meta" class="mt-0.5 text-xs text-ink-secondary">{{ item.meta }}</p>
            </li>
          </ul>
          <p v-else class="py-6 text-center text-sm text-ink-secondary">No recent activity recorded.</p>
          <div class="mt-4 border-t border-border pt-3">
            <VButton size="sm" variant="secondary" @click="router.push({ name: 'platform-logs' })">
              View audit logs
            </VButton>
          </div>
        </VCard>
      </section>
    </template>
  </div>
</template>
