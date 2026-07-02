<script setup>
import { onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { useElectionAdministrators } from "@/composables/useElectionAdministrators";
import { useToast } from "@/composables/useToast";
import { securityApi } from "@/api/security";
import { settingsRoutes as r } from "@/config/settingsRoutes";
import { settingsNav } from "@/config/moduleNav";
import {
  EmptyState,
  LoadingSkeleton,
  ModuleNav,
  PageHeader,
  StatusBadge,
  VAlert,
  VButton,
  VCard,
  VInput,
  VTable,
} from "@/components/ui";

const router = useRouter();
const toast = useToast();

const {
  administrators,
  loading,
  actionLoading,
  error,
  totalCount,
  activeCount,
  loadAdministrators,
  createAdministrator,
  setActiveStatus,
  resetMfa,
} = useElectionAdministrators();

const showCreateForm = ref(false);
const activity = ref([]);
const activityLoading = ref(false);

const createForm = reactive({
  first_name: "",
  last_name: "",
  email: "",
  phone_number: "",
  password: "",
});

const columns = [
  { key: "name", label: "Name" },
  { key: "email", label: "Email" },
  { key: "status", label: "Status" },
  { key: "actions", label: "Actions" },
];

onMounted(async () => {
  await Promise.all([loadAdministrators(), loadActivity()]);
});

async function loadActivity() {
  activityLoading.value = true;
  try {
    const logs = await securityApi.listAuditLogs({ event_type: "admin_action", hours: 168 });
    activity.value = (logs || [])
      .filter((log) => !log.election_uuid)
      .slice(0, 8)
      .map((log) => ({
        id: log.audit_id,
        title: formatActivityTitle(log),
        meta: log.timestamp ? new Date(log.timestamp).toLocaleString() : "",
      }));
  } catch {
    activity.value = [];
  } finally {
    activityLoading.value = false;
  }
}

function formatActivityTitle(log) {
  const action = log.metadata?.action;
  const map = {
    settings_updated: "Platform defaults updated",
    maintenance_updated: "Maintenance settings updated",
    backup_created: "Backup created",
    provider_tested: "Gateway validated",
  };
  return map[action] || action?.replace(/_/g, " ") || log.event_type;
}

const tableRows = () =>
  administrators.value.map((user) => ({
    uuid: user.uuid,
    name: `${user.first_name} ${user.last_name}`.trim(),
    email: user.email,
    status: user.is_active ? "Active" : "Suspended",
    is_active: user.is_active,
  }));

async function submitCreate() {
  try {
    await createAdministrator({ ...createForm });
    toast.success("Election administrator created.");
    showCreateForm.value = false;
    Object.assign(createForm, {
      first_name: "",
      last_name: "",
      email: "",
      phone_number: "",
      password: "",
    });
  } catch {
    /* error surfaced in composable */
  }
}

async function toggleSuspend(user) {
  try {
    await setActiveStatus(user.uuid, !user.is_active);
    toast.success(user.is_active ? "Administrator suspended." : "Administrator reactivated.");
  } catch {
    /* handled in composable */
  }
}

async function handleResetMfa(user) {
  try {
    await resetMfa(user.uuid);
    toast.success("Administrator verification reset. They must complete MFA on next sign-in.");
  } catch {
    /* handled in composable */
  }
}
</script>

<template>
  <div class="vb-page space-y-section">
    <PageHeader
      title="Election administration"
      subtitle="Manage Election Administrators who configure and run elections. Super Admins govern the platform — not individual elections."
      :breadcrumbs="[{ label: 'Settings', to: r.overview }, { label: 'Election Governance', to: r.governance.hub }, { label: 'Election administrators' }]"
    />
    <ModuleNav :items="settingsNav" />

    <VAlert v-if="error" variant="error">{{ error }}</VAlert>

    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <VCard title="Election administrators" :subtitle="`${activeCount} active of ${totalCount}`">
        <VButton size="sm" variant="secondary" @click="showCreateForm = !showCreateForm">
          {{ showCreateForm ? "Hide form" : "Create administrator" }}
        </VButton>
      </VCard>
      <VCard title="Suspend administrator" subtitle="Deactivate accounts without deleting history.">
        <p class="text-sm text-slate-600">Use the table below to suspend or reactivate officers.</p>
      </VCard>
      <VCard title="Reset administrator MFA" subtitle="Force re-verification on next login.">
        <p class="text-sm text-slate-600">Clears verified status so step-up and MFA flows re-run.</p>
      </VCard>
      <VCard title="Administrator activity" subtitle="Platform governance sign-ins and actions.">
        <VButton size="sm" variant="ghost" @click="router.push('/dashboard/platform/logs')">
          Full audit log
        </VButton>
      </VCard>
    </div>

    <VCard v-if="showCreateForm" title="Create election administrator">
      <form class="grid grid-cols-1 gap-4 md:grid-cols-2" @submit.prevent="submitCreate">
        <VInput v-model="createForm.first_name" label="First name" required />
        <VInput v-model="createForm.last_name" label="Last name" required />
        <VInput v-model="createForm.email" label="Email" type="email" required />
        <VInput v-model="createForm.phone_number" label="Phone number" />
        <VInput v-model="createForm.password" label="Temporary password" type="password" required />
        <div class="flex items-end">
          <VButton type="submit" variant="primary" :loading="actionLoading">Create administrator</VButton>
        </div>
      </form>
    </VCard>

    <VCard title="Election administrators">
      <LoadingSkeleton v-if="loading" variant="list" :rows="5" />
      <VTable
        v-else-if="administrators.length"
        :columns="columns"
        :rows="tableRows()"
        empty-text="No election administrators found."
      >
        <template #cell-status="{ row }">
          <StatusBadge :status="row.is_active ? 'open' : 'closed'" />
        </template>
        <template #cell-actions="{ row }">
          <div class="flex flex-wrap gap-2">
            <VButton size="sm" variant="secondary" @click="toggleSuspend(row)">
              {{ row.is_active ? "Suspend" : "Reactivate" }}
            </VButton>
            <VButton size="sm" variant="ghost" @click="handleResetMfa(row)">Reset MFA</VButton>
          </div>
        </template>
      </VTable>
      <EmptyState v-else title="No election administrators" description="Create an administrator to manage elections." />
    </VCard>

    <VCard id="activity" title="Administrator activity" subtitle="Recent platform administration events">
      <LoadingSkeleton v-if="activityLoading" variant="list" :rows="4" />
      <ul v-else-if="activity.length" class="divide-y divide-border">
        <li v-for="item in activity" :key="item.id" class="py-3">
          <p class="text-sm font-medium text-slate-800">{{ item.title }}</p>
          <p v-if="item.meta" class="mt-0.5 text-xs text-slate-500">{{ item.meta }}</p>
        </li>
      </ul>
      <EmptyState v-else title="No recent activity" description="Platform administration events will appear here." />
    </VCard>
  </div>
</template>
