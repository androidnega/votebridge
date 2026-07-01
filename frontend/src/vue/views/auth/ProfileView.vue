<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { VAlert, VButton, VCard, VInput, VTable } from "@/components/ui";
import { useAuthStore } from "@/stores/auth";
import { useToast } from "@/composables/useToast";
import { toastMessages } from "@/config/toastMessages";

const router = useRouter();
const authStore = useAuthStore();
const toast = useToast();

const editing = ref(false);
const saveError = ref("");
const form = reactive({
  first_name: "",
  last_name: "",
  phone_number: "",
});

const sessionColumns = [
  { key: "ip_address", label: "IP address" },
  { key: "last_activity_at", label: "Last active" },
  { key: "is_active", label: "Status" },
];

const profileRows = computed(() => {
  const user = authStore.user;
  if (!user) return [];
  return [
    { label: "Full name", value: authStore.fullName || "—" },
    { label: "Email", value: user.email || "—" },
    { label: "Index number", value: user.index_number || "—" },
    { label: "Role", value: authStore.roleDisplay || "—" },
    { label: "Phone", value: user.phone_number || "—" },
    { label: "Verified", value: user.is_verified ? "Yes" : "No" },
    { label: "Status", value: user.is_active ? "Active" : "Inactive" },
  ];
});

onMounted(async () => {
  if (!authStore.user) {
    try {
      await authStore.fetchProfile();
    } catch (error) {
      toast.error(error.message);
    }
  }
  syncForm();
  authStore.fetchSessions().catch(() => {});
});

function syncForm() {
  form.first_name = authStore.user?.first_name || "";
  form.last_name = authStore.user?.last_name || "";
  form.phone_number = authStore.user?.phone_number || "";
}

function startEditing() {
  syncForm();
  editing.value = true;
  saveError.value = "";
}

async function saveProfile() {
  saveError.value = "";
  try {
    await authStore.updateProfile({
      first_name: form.first_name.trim(),
      last_name: form.last_name.trim(),
      phone_number: form.phone_number.trim(),
    });
    editing.value = false;
    toast.success(toastMessages.profile.updated);
  } catch (error) {
    saveError.value = error.message;
  }
}

async function handleLogout() {
  await authStore.logout();
  toast.info("You have been signed out.");
  router.push({ name: "auth-login" });
}

function formatDate(value) {
  if (!value) return "—";
  return new Date(value).toLocaleString();
}
</script>

<template>
  <div class="mx-auto max-w-4xl space-y-6">
    <div class="flex flex-wrap items-start justify-between gap-4">
      <div>
        <h2 class="text-2xl font-bold text-slate-900">Profile</h2>
        <p class="mt-1 text-sm text-slate-500">Manage your account and active sessions.</p>
      </div>
      <VButton variant="danger" :loading="authStore.loading" @click="handleLogout">
        Sign out
      </VButton>
    </div>

    <VAlert v-if="saveError" variant="error" dismissible @dismiss="saveError = ''">
      {{ saveError }}
    </VAlert>

    <VCard title="Account details">
      <div v-if="authStore.loading && !authStore.user" class="text-sm text-slate-500">
        Loading profile...
      </div>

      <template v-else-if="!editing">
        <dl class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div v-for="row in profileRows" :key="row.label" class="rounded-lg bg-slate-50 p-4">
            <dt class="text-xs font-medium uppercase tracking-wide text-slate-500">
              {{ row.label }}
            </dt>
            <dd class="mt-1 text-sm font-medium text-slate-900">{{ row.value }}</dd>
          </div>
        </dl>
        <div class="mt-4">
          <VButton variant="secondary" @click="startEditing">Edit profile</VButton>
        </div>
      </template>

      <form v-else class="space-y-4" @submit.prevent="saveProfile">
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <VInput v-model="form.first_name" label="First name" required />
          <VInput v-model="form.last_name" label="Last name" required />
        </div>
        <VInput v-model="form.phone_number" label="Phone number" />
        <div class="flex flex-wrap gap-3">
          <VButton type="submit" :loading="authStore.loading">Save changes</VButton>
          <VButton type="button" variant="secondary" @click="editing = false">Cancel</VButton>
        </div>
      </form>
    </VCard>

    <VCard title="Ballot verification" subtitle="Confirm your vote was recorded without revealing your choices">
      <p class="text-sm text-slate-600">
        Use your Secure Voting Token after voting to verify that your ballot was sealed correctly.
      </p>
      <div class="mt-4">
        <VButton variant="secondary" @click="router.push({ name: 'profile-verify-ballot' })">
          Verify ballot
        </VButton>
      </div>
    </VCard>

    <VCard title="Active sessions" subtitle="Devices currently signed in to your account">
      <VTable
        :columns="sessionColumns"
        :rows="authStore.sessions"
        :loading="authStore.sessionsLoading"
        empty-text="No active sessions found."
      >
        <template #cell-last_activity_at="{ value }">
          {{ formatDate(value) }}
        </template>
        <template #cell-is_active="{ value }">
          <span
            class="inline-flex rounded-full px-2 py-0.5 text-xs font-medium"
            :class="value ? 'bg-green-50 text-green-700' : 'bg-slate-100 text-slate-600'"
          >
            {{ value ? "Active" : "Inactive" }}
          </span>
        </template>
      </VTable>
    </VCard>
  </div>
</template>
