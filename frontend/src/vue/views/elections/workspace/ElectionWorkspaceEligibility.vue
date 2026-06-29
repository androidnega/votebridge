<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { EmptyState, LoadingSkeleton, VAlert, VButton, VCard, VInput, VTable, ConfirmDialog } from "@/components/ui";
import { emptyStates } from "@/config/emptyStates";
import { toastMessages } from "@/config/toastMessages";
import { useToast } from "@/composables/useToast";
import { electionsApi } from "@/api/elections";
import { usersApi } from "@/api/users";
import { extractApiError } from "@/api/helpers";

const route = useRoute();
const toast = useToast();
const electionUuid = computed(() => route.params.uuid);

const records = ref([]);
const searchResults = ref([]);
const selectedUsers = ref([]);
const loading = ref(false);
const searching = ref(false);
const saving = ref(false);
const error = ref(null);
const pendingRemove = ref(null);
const hasSearched = ref(false);

const filters = ref({
  indexNumber: "",
  name: "",
  programmeCode: "",
});

const columns = [
  { key: "user_name", label: "Voter" },
  { key: "user_index_number", label: "Index number" },
  { key: "user_email", label: "Email" },
  { key: "is_eligible", label: "Eligible" },
  { key: "actions", label: "" },
];

const searchColumns = [
  { key: "name", label: "Name" },
  { key: "index_number", label: "Index" },
  { key: "email", label: "Email" },
  { key: "actions", label: "" },
];

const eligibleForm = ref({
  eligibility_reason: "Registered student voter",
  is_eligible: true,
});

function displayName(user) {
  return `${user.first_name || ""} ${user.last_name || ""}`.trim() || user.email;
}

function matchesProgrammeFilter(user) {
  const code = filters.value.programmeCode.trim().toUpperCase();
  if (!code) return true;
  return (user.index_number || "").toUpperCase().includes(code);
}

async function loadRecords() {
  loading.value = true;
  error.value = null;
  try {
    const result = await electionsApi.listEligibility(electionUuid.value, {
      search: filters.value.name || filters.value.indexNumber || undefined,
    });
    records.value = result.items;
  } catch (err) {
    error.value = extractApiError(err);
  } finally {
    loading.value = false;
  }
}

async function searchStudents() {
  searching.value = true;
  hasSearched.value = true;
  error.value = null;
  try {
    const query = [filters.value.indexNumber, filters.value.name, filters.value.programmeCode]
      .filter(Boolean)
      .join(" ")
      .trim();
    const result = await usersApi.list({
      search: query || undefined,
      role: "student",
      is_active: true,
    });
    searchResults.value = result.items
      .filter(matchesProgrammeFilter)
      .map((user) => ({
        ...user,
        name: displayName(user),
      }));
  } catch (err) {
    error.value = extractApiError(err);
  } finally {
    searching.value = false;
  }
}

function toggleSelect(user) {
  const exists = selectedUsers.value.find((u) => u.uuid === user.uuid);
  if (exists) {
    selectedUsers.value = selectedUsers.value.filter((u) => u.uuid !== user.uuid);
  } else {
    selectedUsers.value = [...selectedUsers.value, user];
  }
}

async function addSingle(user) {
  saving.value = true;
  try {
    await electionsApi.createEligibility(electionUuid.value, {
      user_uuid: user.uuid,
      is_eligible: eligibleForm.value.is_eligible,
      eligibility_reason: eligibleForm.value.eligibility_reason,
    });
    toast.success(toastMessages.eligibility.added);
    await loadRecords();
  } catch (err) {
    error.value = extractApiError(err);
  } finally {
    saving.value = false;
  }
}

async function bulkAddSelected() {
  if (!selectedUsers.value.length) return;
  saving.value = true;
  try {
    await electionsApi.bulkEligibility(electionUuid.value, {
      user_uuids: selectedUsers.value.map((u) => u.uuid),
      is_eligible: eligibleForm.value.is_eligible,
      eligibility_reason: eligibleForm.value.eligibility_reason,
    });
    toast.success(toastMessages.eligibility.bulkAdded(selectedUsers.value.length));
    selectedUsers.value = [];
    await loadRecords();
  } catch (err) {
    error.value = extractApiError(err);
  } finally {
    saving.value = false;
  }
}

function askRemoveRecord(row) {
  pendingRemove.value = {
    title: "Remove voter",
    description: `Remove ${row.user_name || row.user_index_number} from the voter roll?`,
    row,
  };
}

async function removeRecord(row) {
  await electionsApi.deleteEligibility(electionUuid.value, row.uuid);
  toast.success(toastMessages.eligibility.removed);
  await loadRecords();
}

const confirmRemoveOpen = computed({
  get: () => Boolean(pendingRemove.value),
  set: (value) => {
    if (!value) pendingRemove.value = null;
  },
});

async function confirmRemove() {
  if (!pendingRemove.value?.row) return;
  await removeRecord(pendingRemove.value.row);
  pendingRemove.value = null;
}

onMounted(loadRecords);
watch(() => electionUuid.value, loadRecords);
</script>

<template>
  <div class="space-y-section">
    <VAlert v-if="error" variant="error">{{ error }}</VAlert>

    <VCard title="Find students">
      <p class="mb-4 text-sm text-slate-600">
        Search by index number or name. Use the programme code field to narrow results (e.g. ITS, ITD).
      </p>
      <div class="grid grid-cols-1 gap-4 md:grid-cols-3">
        <VInput v-model="filters.indexNumber" label="Index number" placeholder="BC/ITS/24/047" />
        <VInput v-model="filters.name" label="Student name" placeholder="Kwame Mensah" />
        <VInput v-model="filters.programmeCode" label="Programme code" placeholder="ITS" />
      </div>
      <div class="mt-4 flex flex-wrap gap-2">
        <VButton variant="secondary" :loading="searching" @click="searchStudents">Search</VButton>
        <VButton :loading="saving" :disabled="!selectedUsers.length" @click="bulkAddSelected">
          Add selected ({{ selectedUsers.length }})
        </VButton>
      </div>
    </VCard>

    <VCard v-if="searchResults.length" padding="none" title="Search results">
      <VTable :columns="searchColumns" :rows="searchResults" :loading="searching">
        <template #cell-actions="{ row }">
          <div class="flex gap-1">
            <VButton size="sm" variant="secondary" @click="addSingle(row)">Add</VButton>
            <VButton size="sm" variant="ghost" @click="toggleSelect(row)">
              {{ selectedUsers.some((u) => u.uuid === row.uuid) ? "Selected" : "Select" }}
            </VButton>
          </div>
        </template>
      </VTable>
    </VCard>

    <VCard v-else-if="searching" padding="compact">
      <LoadingSkeleton variant="list" :rows="3" />
    </VCard>

    <EmptyState
      v-if="hasSearched && !searching && !searchResults.length"
      v-bind="emptyStates.searchStudents"
    />

    <VCard title="Voter roll" padding="none">
      <LoadingSkeleton v-if="loading && !records.length" variant="list" :rows="4" class="p-card" />
      <VTable v-else-if="records.length" :columns="columns" :rows="records" :loading="loading">
        <template #cell-is_eligible="{ row }">{{ row.is_eligible ? "Yes" : "No" }}</template>
        <template #cell-actions="{ row }">
          <VButton size="sm" variant="ghost" @click="askRemoveRecord(row)">Remove</VButton>
        </template>
      </VTable>
      <EmptyState v-else v-bind="emptyStates.eligibility" class="p-card" />
    </VCard>

    <ConfirmDialog
      v-model="confirmRemoveOpen"
      :title="pendingRemove?.title || 'Remove voter'"
      :description="pendingRemove?.description || ''"
      variant="danger"
      icon="profile"
      confirm-label="Remove"
      @confirm="confirmRemove"
    />
  </div>
</template>
