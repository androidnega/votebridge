<script setup>
import { onMounted, onUnmounted } from "vue";
import { ConnectionStatusIndicator, StatCard } from "@/components/dashboard";
import { operationsNav } from "@/config/moduleNav";
import { LoadingSkeleton, ModuleNav, PageHeader, VAlert, VTable } from "@/components/ui";
import { useOperationsStore } from "@/stores/operations";

const store = useOperationsStore();

const columns = [
  { key: "user_name", label: "User" },
  { key: "role", label: "Role" },
  { key: "ip_address", label: "IP" },
  { key: "last_activity_at", label: "Last activity" },
];

onMounted(() => {
  store.fetchSessions().catch(() => {});
  store.connectRealtime();
});

onUnmounted(() => store.disconnectRealtime());
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="Users & sessions"
      subtitle="Authenticated sessions and online role distribution."
      :breadcrumbs="[{ label: 'Overview', to: '/' }, { label: 'Operations', to: '/operations' }, { label: 'Users & Sessions' }]"
    >
      <template #actions>
        <ConnectionStatusIndicator :status="store.realtimeStatus" />
      </template>
    </PageHeader>

    <ModuleNav :items="operationsNav" />
    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>
    <LoadingSkeleton v-if="store.loading && !store.sessions" variant="stats" :rows="4" />

    <template v-else-if="store.sessions">
      <section class="grid grid-cols-1 gap-4 xs:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Students online" :value="store.sessions.students_online ?? 0" accent="brand" />
        <StatCard label="Candidates online" :value="store.sessions.candidates_online ?? 0" accent="green" />
        <StatCard label="Admins online" :value="store.sessions.admins_online ?? 0" accent="slate" />
        <StatCard label="Super admins" :value="store.sessions.super_admins_online ?? 0" accent="amber" />
        <StatCard label="Active sessions" :value="store.sessions.authenticated_sessions ?? 0" accent="brand" />
        <StatCard label="Expired" :value="store.sessions.expired_sessions ?? 0" accent="amber" />
        <StatCard label="Blocked" :value="store.sessions.blocked_sessions ?? 0" accent="red" />
        <StatCard label="Multi-device" :value="store.sessions.multiple_device_sessions ?? 0" accent="red" />
      </section>

      <VTable :columns="columns" :rows="store.sessions.recent_sessions || []" empty-text="No active sessions." />
    </template>
  </div>
</template>
