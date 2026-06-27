<script setup>
import { computed } from "vue";
import { StatusBadge, VCard } from "@/components/ui";

const props = defineProps({
  device: { type: Object, default: null },
  sessionStatus: { type: Object, default: null },
  loading: { type: Boolean, default: false },
});

const trustVariant = computed(() => {
  const level = props.device?.trust_level;
  if (level === "HIGH") return "success";
  if (level === "MEDIUM") return "scheduled";
  if (level === "LOW") return "warning";
  if (level === "REVOKED") return "danger";
  return "grey";
});

const deviceTypeLabel = computed(() => {
  if (props.device?.device_type === "university_managed") return "University managed";
  return "Personal device";
});

function formatRemaining(seconds) {
  if (!seconds) return "—";
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}m ${secs}s`;
}
</script>

<template>
  <VCard title="This device">
    <div v-if="loading" class="text-sm text-slate-500">Loading…</div>
    <div v-else-if="device" class="space-y-4">
      <div class="flex flex-wrap items-center gap-2">
        <StatusBadge variant="success" label="Current" />
        <StatusBadge :variant="trustVariant" :label="device.trust_level || 'Unknown'" />
        <StatusBadge variant="grey" :label="deviceTypeLabel" />
      </div>

      <p class="font-medium text-brand">{{ device.device_name }}</p>

      <dl class="grid grid-cols-2 gap-3 text-sm md:grid-cols-3">
        <div>
          <dt class="text-slate-500">Risk score</dt>
          <dd>{{ Math.round(device.risk_score ?? 0) }} / 100</dd>
        </div>
        <div>
          <dt class="text-slate-500">Trust expires</dt>
          <dd>{{ device.expires_at ? new Date(device.expires_at).toLocaleDateString() : "—" }}</dd>
        </div>
        <div>
          <dt class="text-slate-500">Last login</dt>
          <dd>
            {{
              device.login_summary?.last_login
                ? new Date(device.login_summary.last_login).toLocaleString()
                : device.last_seen
                  ? new Date(device.last_seen).toLocaleString()
                  : "—"
            }}
          </dd>
        </div>
        <div>
          <dt class="text-slate-500">Previous login</dt>
          <dd>
            {{
              device.login_summary?.previous_login || device.previous_login_at
                ? new Date(device.login_summary?.previous_login || device.previous_login_at).toLocaleString()
                : "—"
            }}
          </dd>
        </div>
        <div>
          <dt class="text-slate-500">Location</dt>
          <dd>{{ device.last_city || device.last_country || "—" }}</dd>
        </div>
        <div>
          <dt class="text-slate-500">Browser</dt>
          <dd>{{ device.browser_name }} {{ device.browser_version }}</dd>
        </div>
        <div>
          <dt class="text-slate-500">System</dt>
          <dd>{{ device.operating_system }}</dd>
        </div>
        <div>
          <dt class="text-slate-500">Last verified</dt>
          <dd>{{ device.last_verified ? new Date(device.last_verified).toLocaleString() : "—" }}</dd>
        </div>
      </dl>

      <div
        v-if="sessionStatus?.enabled"
        class="rounded-input border border-border bg-surface-muted p-4 text-sm"
      >
        <div class="flex flex-wrap items-center gap-2">
          <span class="font-medium text-slate-700">Session status</span>
          <StatusBadge
            :variant="sessionStatus.active ? 'success' : 'grey'"
            :label="sessionStatus.active ? 'High assurance' : 'Standard'"
          />
        </div>
        <p v-if="sessionStatus.active" class="mt-2 text-slate-600">
          Remaining: {{ formatRemaining(sessionStatus.remaining_seconds) }}
        </p>
        <p v-if="sessionStatus.protected_actions_available" class="mt-1 text-slate-600">
          Protected actions available (strongroom, certification, system control).
        </p>
      </div>
    </div>
    <p v-else class="text-sm text-slate-600">
      This browser is not registered as a trusted device. Biometric verification will be required at next login.
    </p>
  </VCard>
</template>
