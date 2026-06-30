<script setup>
import { computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { LoadingSkeleton, VCard } from "@/components/ui";
import { useOperationsStore } from "@/stores/operations";

const router = useRouter();
const operationsStore = useOperationsStore();

const widgets = computed(() => {
  const overview = operationsStore.overview || {};
  const health = overview.health || {};
  const queues = overview.queues || {};
  const ussd = overview.ussd || {};
  const realtime = overview.realtime || {};

  function statusTone(value, inverted = false) {
    if (value === "healthy" || value === "connected" || value === "ok") {
      return inverted ? "danger" : "success";
    }
    if (value === "degraded" || value === "warning") return "warning";
    return inverted ? "success" : "danger";
  }

  return [
    {
      label: "System health",
      value: health.status_label || health.status || "Unknown",
      hint: health.summary || "Infrastructure status",
      to: "/dashboard/operations/health",
      tone: statusTone((health.status || "").toLowerCase()),
    },
    {
      label: "Realtime status",
      value: realtime.status_label || realtime.status || "Offline",
      hint: `${realtime.active_connections ?? 0} active connections`,
      to: "/dashboard/operations/activity",
      tone: statusTone((realtime.status || "").toLowerCase()),
    },
    {
      label: "Queue status",
      value: queues.status_label || queues.status || "Idle",
      hint: `${queues.pending ?? 0} pending jobs`,
      to: "/dashboard/operations/queues",
      tone: statusTone((queues.status || "ok").toLowerCase()),
    },
    {
      label: "USSD status",
      value: ussd.status_label || ussd.status || "Inactive",
      hint: `${ussd.active_sessions ?? 0} active sessions`,
      to: "/dashboard/ussd",
      tone: statusTone((ussd.status || "").toLowerCase()),
    },
    {
      label: "WebSocket",
      value: realtime.websocket_status || realtime.status || "Unknown",
      hint: "Live channel connectivity",
      to: "/dashboard/operations/infrastructure",
      tone: statusTone((realtime.websocket_status || realtime.status || "").toLowerCase()),
    },
    {
      label: "Notification queue",
      value: queues.notifications_status || queues.status_label || "Unknown",
      hint: `${queues.notifications_pending ?? queues.pending ?? 0} messages waiting`,
      to: "/dashboard/communications/queue",
      tone: statusTone((queues.notifications_status || "ok").toLowerCase()),
    },
  ];
});

const toneClasses = {
  success: "border-success-200 bg-success-50 text-success-800",
  warning: "border-warning-200 bg-warning-50 text-warning-800",
  danger: "border-danger-200 bg-danger-50 text-danger-800",
};

onMounted(() => {
  if (!operationsStore.overview) {
    operationsStore.fetchOverview().catch(() => {});
  }
});

function openWidget(widget) {
  router.push(widget.to);
}
</script>

<template>
  <section>
    <div class="mb-4 flex items-center justify-between gap-3">
      <div>
        <h3 class="text-lg font-semibold text-slate-900">System health</h3>
        <p class="text-sm text-slate-500">Platform status at a glance. Select a tile for details.</p>
      </div>
    </div>

    <LoadingSkeleton v-if="operationsStore.loading && !operationsStore.overview" variant="stats" :rows="3" />

    <div v-else class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
      <button
        v-for="widget in widgets"
        :key="widget.label"
        type="button"
        class="rounded-xl border p-card text-left shadow-sm transition hover:shadow-md focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-500"
        :class="toneClasses[widget.tone] || toneClasses.success"
        @click="openWidget(widget)"
      >
        <p class="text-sm font-medium opacity-80">{{ widget.label }}</p>
        <p class="mt-1 text-xl font-semibold">{{ widget.value }}</p>
        <p class="mt-1 text-xs opacity-75">{{ widget.hint }}</p>
      </button>
    </div>
  </section>
</template>
