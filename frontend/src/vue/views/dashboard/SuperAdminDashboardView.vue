<script setup>
import { computed, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import {
  ConnectionStatusIndicator,
  LiveFraudFeed,
  LiveSecurityFeed,
  LoadingSkeleton,
  StatCard,
} from "@/components/dashboard";
import { VAlert, VButton } from "@/components/ui";
import { useDashboardRealtime } from "@/composables/useDashboardRealtime";
import { useDashboardStore } from "@/stores/dashboard";
import { useFraudStore } from "@/stores/fraud";
import { useSecurityStore } from "@/stores/security";

const router = useRouter();
const dashboardStore = useDashboardStore();
const securityStore = useSecurityStore();
const fraudStore = useFraudStore();
const realtime = useDashboardRealtime("super-admin");

const monitoring = computed(() => dashboardStore.monitoringSummary || {});
const fraud = computed(() => fraudStore.integrityReport || dashboardStore.fraudIntegrity || {});
const alerts = computed(() => monitoring.value.alerts || {});

const systemHealthScore = computed(() => {
  const audit = monitoring.value.audit?.total_24h ?? 0;
  const openAlerts = alerts.value.open ?? 0;
  if (openAlerts === 0 && audit > 0) return "Healthy";
  if (openAlerts > 5) return "Attention";
  return "Stable";
});

const securityFeedItems = computed(() => {
  if (securityStore.alertsFeed.length) return securityStore.alertsFeed.slice(0, 8);
  return dashboardStore.securityFeed?.alerts?.slice(0, 8) || [];
});

const fraudFeedItems = computed(() => fraudStore.casesFeed.slice(0, 8));

onMounted(() => {
  dashboardStore.fetchSuperAdminDashboard().catch(() => {});
  securityStore.fetchSecurityFeed().catch(() => {});
  fraudStore.fetchFraudFeed().catch(() => {});
  securityStore.connectRealtime();
  fraudStore.connectRealtime();
});

onUnmounted(() => {
  securityStore.disconnectRealtime();
  fraudStore.disconnectRealtime();
});
</script>

<template>
  <div class="space-y-8">
    <div class="flex flex-wrap items-start justify-between gap-4">
      <div>
        <div class="flex flex-wrap items-center gap-3">
          <h2 class="text-2xl font-bold text-slate-900">System command center</h2>
          <ConnectionStatusIndicator
            :status="realtime.status.value"
            :label="realtime.label.value"
          />
        </div>
        <p class="mt-1 text-sm text-slate-500">Platform health, users, and security posture.</p>
      </div>
      <VButton variant="secondary" size="sm" @click="router.push('/fraud')">Fraud dashboard</VButton>
    </div>

    <VAlert v-if="dashboardStore.error" variant="error">{{ dashboardStore.error }}</VAlert>

    <LoadingSkeleton v-if="dashboardStore.loading && !monitoring.audit" variant="stats" :rows="4" />

    <section class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <StatCard
        label="System health"
        :value="systemHealthScore"
        :hint="`${monitoring.audit?.total_24h ?? 0} audit events (24h)`"
        :loading="dashboardStore.loading"
        accent="green"
      />
      <StatCard
        label="Active users"
        :value="dashboardStore.activeUsersCount"
        :loading="dashboardStore.loading"
        accent="brand"
      />
      <StatCard
        label="Elections"
        :value="dashboardStore.totalElectionsCount"
        :loading="dashboardStore.loading"
        accent="slate"
      />
      <StatCard
        label="Open alerts"
        :value="alerts.open ?? 0"
        :loading="dashboardStore.loading"
        accent="red"
      />
    </section>

    <section class="grid grid-cols-1 gap-6 lg:grid-cols-2">
      <div class="rounded-xl bg-white p-6 shadow-sm ring-1 ring-slate-900/5">
        <h3 class="text-lg font-semibold text-slate-900">Security summary</h3>
        <dl class="mt-4 grid grid-cols-2 gap-4 text-sm">
          <div class="rounded-lg bg-slate-50 p-4">
            <dt class="text-slate-500">Audit (24h)</dt>
            <dd class="mt-1 text-xl font-semibold">{{ monitoring.audit?.total_24h ?? 0 }}</dd>
          </div>
          <div class="rounded-lg bg-slate-50 p-4">
            <dt class="text-slate-500">Devices (24h)</dt>
            <dd class="mt-1 text-xl font-semibold">{{ monitoring.devices?.total_24h ?? 0 }}</dd>
          </div>
          <div class="rounded-lg bg-slate-50 p-4">
            <dt class="text-slate-500">Locations (24h)</dt>
            <dd class="mt-1 text-xl font-semibold">{{ monitoring.locations?.total_24h ?? 0 }}</dd>
          </div>
          <div class="rounded-lg bg-slate-50 p-4">
            <dt class="text-slate-500">Escalated</dt>
            <dd class="mt-1 text-xl font-semibold">{{ alerts.escalated ?? 0 }}</dd>
          </div>
        </dl>
      </div>

      <div class="rounded-xl bg-white p-6 shadow-sm ring-1 ring-slate-900/5">
        <h3 class="text-lg font-semibold text-slate-900">Fraud summary</h3>
        <dl class="mt-4 grid grid-cols-2 gap-4 text-sm">
          <div class="rounded-lg bg-amber-50 p-4">
            <dt class="text-amber-700">Open cases</dt>
            <dd class="mt-1 text-xl font-semibold text-amber-900">{{ fraud.open_cases ?? 0 }}</dd>
          </div>
          <div class="rounded-lg bg-green-50 p-4">
            <dt class="text-green-700">Resolved</dt>
            <dd class="mt-1 text-xl font-semibold text-green-900">{{ fraud.resolved_cases ?? 0 }}</dd>
          </div>
          <div class="rounded-lg bg-orange-50 p-4">
            <dt class="text-orange-700">High risk</dt>
            <dd class="mt-1 text-xl font-semibold text-orange-900">{{ fraud.high_risk_cases ?? 0 }}</dd>
          </div>
          <div class="rounded-lg bg-red-50 p-4">
            <dt class="text-red-700">Critical</dt>
            <dd class="mt-1 text-xl font-semibold text-red-900">{{ fraud.critical_cases ?? 0 }}</dd>
          </div>
        </dl>
      </div>
    </section>

    <section class="grid grid-cols-1 gap-6 lg:grid-cols-2">
      <LiveSecurityFeed
        :items="securityFeedItems"
        :loading="securityStore.loading && !securityFeedItems.length"
        :status="securityStore.realtimeStatus"
      />
      <LiveFraudFeed
        :items="fraudFeedItems"
        :loading="fraudStore.loading && !fraudFeedItems.length"
        :status="fraudStore.realtimeStatus"
      />
    </section>
  </div>
</template>
