<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import CurrentDeviceCard from "@/components/trusted-devices/CurrentDeviceCard.vue";
import DeviceRenameDialog from "@/components/trusted-devices/DeviceRenameDialog.vue";
import {
  EmptyState,
  LoadingSkeleton,
  PageHeader,
  StatusBadge,
  VAlert,
  VButton,
  VCard,
  VModal,
  VTable,
} from "@/components/ui";
import { useTrustedDevicesStore } from "@/stores/trustedDevices";
import { useToast } from "@/composables/useToast";
import { useAuthStore } from "@/stores/auth";

const store = useTrustedDevicesStore();
const auth = useAuthStore();
const toast = useToast();
const route = useRoute();

const isStrongroom = computed(() => route.path.startsWith("/strongroom"));
const breadcrumbs = computed(() =>
  isStrongroom.value
    ? [
        { label: "Strong room", to: "/strongroom" },
        { label: "Investigations", to: "/strongroom/investigations" },
        { label: "Trusted devices" },
      ]
    : [{ label: "Security", to: "/security" }, { label: "Trusted devices" }]
);

const renameOpen = ref(false);
const revokeOpen = ref(false);
const historyOpen = ref(false);
const selectedDevice = ref(null);
const historyRows = ref([]);

const columns = [
  { key: "device_name", label: "Device" },
  { key: "trust_level", label: "Trust" },
  { key: "risk_score", label: "Risk" },
  { key: "device_type", label: "Type" },
  { key: "expires_at", label: "Expires" },
  { key: "last_seen", label: "Last login" },
  { key: "status", label: "Status" },
  { key: "actions", label: "" },
];

const isSuperAdmin = auth.isSuperAdmin;

onMounted(async () => {
  await Promise.all([
    store.fetchDevices(),
    store.fetchCurrentDevice(),
    store.fetchSessionStatus(),
  ]);
});

function trustVariant(level) {
  if (level === "HIGH") return "success";
  if (level === "MEDIUM") return "scheduled";
  if (level === "LOW") return "warning";
  if (level === "REVOKED") return "danger";
  return "grey";
}

function deviceTypeLabel(type) {
  return type === "university_managed" ? "University" : "Personal";
}

function openRename(device) {
  selectedDevice.value = device;
  renameOpen.value = true;
}

function openRevoke(device) {
  selectedDevice.value = device;
  revokeOpen.value = true;
}

async function openHistory(device) {
  selectedDevice.value = device;
  historyRows.value = await store.fetchDeviceHistory(device.uuid);
  historyOpen.value = true;
}

async function handleRename(name) {
  if (!selectedDevice.value) return;
  await store.renameDevice(selectedDevice.value.uuid, name);
  toast.success("Device renamed");
  renameOpen.value = false;
}

async function handleRevoke() {
  if (!selectedDevice.value) return;
  await store.revokeDevice(selectedDevice.value.uuid);
  toast.success("Device revoked");
  revokeOpen.value = false;
  await store.fetchCurrentDevice();
  await store.fetchSessionStatus();
}

async function handleAssignUniversity(device) {
  await store.assignUniversity(device.uuid);
  toast.success("Device marked as university managed");
}

async function handleForceReverify() {
  await store.forceReverify();
  toast.info("This device will require biometric verification at next login.");
  await store.fetchDevices();
  await store.fetchCurrentDevice();
  await store.fetchSessionStatus();
}
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="Trusted devices"
      subtitle="Manage browsers recognized for streamlined administrator sign-in."
      :breadcrumbs="breadcrumbs"
    />

    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>

    <LoadingSkeleton v-if="store.loading && !store.devices.length" variant="list" :rows="6" />

    <template v-else>
      <CurrentDeviceCard
        :device="store.currentDevice"
        :session-status="store.sessionStatus"
        :loading="store.loading"
        class="mb-section"
      />

      <VCard title="Registered devices" class="mb-section">
        <div class="mb-4 flex flex-wrap gap-3">
          <VButton variant="secondary" :loading="store.actionLoading" @click="handleForceReverify">
            Reverify this device
          </VButton>
        </div>

        <EmptyState
          v-if="!store.devices.length"
          title="No trusted devices"
          description="Complete biometric verification at login to register this browser."
        />

        <VTable v-else :columns="columns" :rows="store.devices" row-key="uuid">
          <template #cell-trust_level="{ row }">
            <StatusBadge :variant="trustVariant(row.trust_level)" :label="row.trust_level || '—'" />
          </template>
          <template #cell-risk_score="{ row }">
            {{ Math.round(row.risk_score ?? 0) }}
          </template>
          <template #cell-device_type="{ row }">
            {{ deviceTypeLabel(row.device_type) }}
          </template>
          <template #cell-expires_at="{ row }">
            {{ row.expires_at ? new Date(row.expires_at).toLocaleDateString() : "—" }}
          </template>
          <template #cell-last_seen="{ row }">
            {{ row.last_seen ? new Date(row.last_seen).toLocaleString() : "—" }}
          </template>
          <template #cell-status="{ row }">
            <StatusBadge v-if="row.is_current" variant="success" label="Current" />
            <StatusBadge v-else-if="row.is_revoked" variant="danger" label="Revoked" />
            <StatusBadge v-else-if="row.is_trusted" variant="scheduled" label="Trusted" />
            <StatusBadge v-else variant="grey" label="Inactive" />
          </template>
          <template #cell-actions="{ row }">
            <div class="flex flex-wrap gap-2">
              <VButton size="sm" variant="ghost" @click="openHistory(row)">History</VButton>
              <VButton size="sm" variant="ghost" @click="openRename(row)">Rename</VButton>
              <VButton
                v-if="isSuperAdmin && row.device_type !== 'university_managed' && !row.is_revoked"
                size="sm"
                variant="ghost"
                @click="handleAssignUniversity(row)"
              >
                University
              </VButton>
              <VButton
                v-if="!row.is_revoked"
                size="sm"
                variant="danger"
                @click="openRevoke(row)"
              >
                Revoke
              </VButton>
            </div>
          </template>
        </VTable>
      </VCard>
    </template>

    <DeviceRenameDialog
      :open="renameOpen"
      :device="selectedDevice"
      :loading="store.actionLoading"
      @close="renameOpen = false"
      @save="handleRename"
    />

    <VModal :open="revokeOpen" title="Revoke trusted device?" @close="revokeOpen = false">
      <p class="text-sm text-slate-600">
        Revoking <strong>{{ selectedDevice?.device_name }}</strong> will terminate active sessions and require biometric verification on next login.
      </p>
      <div class="mt-4 flex justify-end gap-3">
        <VButton variant="secondary" @click="revokeOpen = false">Cancel</VButton>
        <VButton variant="danger" :loading="store.actionLoading" @click="handleRevoke">Revoke</VButton>
      </div>
    </VModal>

    <VModal
      :open="historyOpen"
      :title="`Login history — ${selectedDevice?.device_name || ''}`"
      @close="historyOpen = false"
    >
      <EmptyState
        v-if="!historyRows.length"
        title="No login history"
        description="History appears after trusted logins from this device."
      />
      <ul v-else class="space-y-3 text-sm">
        <li
          v-for="(entry, idx) in historyRows"
          :key="idx"
          class="rounded-input border border-border p-3"
        >
          <p class="font-medium">{{ new Date(entry.logged_in_at).toLocaleString() }}</p>
          <p class="text-slate-600">
            {{ entry.city || entry.country || "Unknown location" }} ·
            {{ entry.browser_name }} · {{ entry.operating_system }}
          </p>
          <p class="text-slate-500">
            {{ entry.authentication_method }} · Risk {{ Math.round(entry.risk_score ?? 0) }}
          </p>
        </li>
      </ul>
    </VModal>
  </div>
</template>
