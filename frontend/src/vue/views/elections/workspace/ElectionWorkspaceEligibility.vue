<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { ElectionWorkspacePageShell } from "@/components/admin";
import { EmptyState, LoadingSkeleton, VAlert, VButton, VCard, VInput, VTable, ConfirmDialog } from "@/components/ui";
import { emptyStates } from "@/config/emptyStates";
import { toastMessages } from "@/config/toastMessages";
import { useClientListPagination } from "@/composables/useClientListPagination";
import { useServerListPagination } from "@/composables/useServerListPagination";
import { useToast } from "@/composables/useToast";
import { electionsApi } from "@/api/elections";
import { usersApi } from "@/api/users";
import { extractApiError } from "@/api/helpers";

const route = useRoute();
const toast = useToast();
const electionUuid = computed(() => route.params.uuid);

const filters = ref({
  indexNumber: "",
  name: "",
  programmeCode: "",
});

const searchResults = ref([]);
const selectedUsers = ref([]);
const searching = ref(false);
const saving = ref(false);
const error = ref(null);
const pendingRemove = ref(null);
const hasSearched = ref(false);

const {
  page: rollPage,
  total: rollTotal,
  totalPages: rollTotalPages,
  rangeLabel: rollRangeLabel,
  items: rollRecords,
  loading,
  load: loadRollRecords,
  goToPage: goToRollPage,
} = useServerListPagination(
  (params) =>
    electionsApi.listEligibility(electionUuid.value, {
      ...params,
      search: filters.value.name || filters.value.indexNumber || undefined,
    }),
  { pageSize: 15 }
);

const {
  page: searchPage,
  total: searchTotal,
  totalPages: searchTotalPages,
  rangeLabel: searchRangeLabel,
  items: pagedSearchResults,
  goToPage: goToSearchPage,
} = useClientListPagination(searchResults, { pageSize: 10 });

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

async function refreshRoll() {
  error.value = null;
  try {
    await loadRollRecords();
  } catch (err) {
    error.value = extractApiError(err);
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
    await refreshRoll();
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
    await refreshRoll();
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
  await refreshRoll();
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

onMounted(refreshRoll);
watch(() => electionUuid.value, refreshRoll);
</script>

<template>
  <ElectionWorkspacePageShell title="Eligibility" subtitle="Manage the voter roll and programme filters for this election.">
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

    <VCard v-if="searchTotal" padding="none" title="Search results" class="vb-list-panel--bounded">
      <VTable
        scrollable
        :columns="searchColumns"
        :rows="pagedSearchResults"
        :loading="searching"
        :page="searchPage"
        :total-pages="searchTotalPages"
        :total="searchTotal"
        :range-label="searchRangeLabel"
        @update:page="goToSearchPage"
      >
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

    <VCard title="Voter roll" padding="none" class="vb-list-panel--bounded">
      <LoadingSkeleton v-if="loading && !rollTotal" variant="list" :rows="4" class="p-card" />
      <VTable
        v-else-if="rollTotal"
        scrollable
        :columns="columns"
        :rows="rollRecords"
        :loading="loading"
        :page="rollPage"
        :total-pages="rollTotalPages"
        :total="rollTotal"
        :range-label="rollRangeLabel"
        @update:page="goToRollPage"
      >
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
  </ElectionWorkspacePageShell>
</template>
