<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { ElectionWorkspacePageShell } from "@/components/admin";
import { ConfirmDialog, EmptyState, LoadingSkeleton, VAlert, VButton, VCard, VInput, VModal, VTable } from "@/components/ui";
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

const quickAdd = ref({
  indexNumber: "",
  phoneNumber: "",
});

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
const importOpen = ref(false);
const importFile = ref(null);
const importing = ref(false);
const importResult = ref(null);

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
  { key: "user_phone_number", label: "Phone" },
  { key: "user_email", label: "Email" },
  { key: "is_eligible", label: "Eligible" },
  { key: "actions", label: "" },
];

const searchColumns = [
  { key: "name", label: "Name" },
  { key: "index_number", label: "Index" },
  { key: "phone_number", label: "Phone" },
  { key: "email", label: "Email" },
  { key: "actions", label: "" },
];

const eligibleForm = ref({
  eligibility_reason: "Registered student voter",
  is_eligible: true,
});

const importForm = ref({
  eligibility_reason: "Registered student voter",
  is_eligible: true,
});

function displayName(user) {
  return `${user.first_name || ""} ${user.last_name || ""}`.trim() || user.email;
}

function normalizeIndex(value = "") {
  return value.trim().toUpperCase().replace(/\s+/g, "");
}

function formatPhone(value) {
  if (!value) return "—";
  const digits = String(value).replace(/\D/g, "");
  if (digits.startsWith("233") && digits.length === 12) {
    return `0${digits.slice(3)}`;
  }
  return value;
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
    const indexQuery = normalizeIndex(filters.value.indexNumber);
    const nameQuery = filters.value.name.trim();
    let result;

    if (indexQuery && !nameQuery) {
      result = await usersApi.list({
        search: indexQuery,
        role: "student,candidate",
        is_active: true,
      });
      const exactMatches = result.items.filter(
        (user) => normalizeIndex(user.index_number || "") === indexQuery
      );
      if (exactMatches.length) {
        result = { ...result, items: exactMatches };
      }
    } else {
      const query = [nameQuery, indexQuery].filter(Boolean).join(" ").trim();
      result = await usersApi.list({
        search: query || undefined,
        role: "student,candidate",
        is_active: true,
      });
    }

    searchResults.value = result.items
      .filter(matchesProgrammeFilter)
      .map((user) => ({
        ...user,
        name: displayName(user),
        phone_number: formatPhone(user.phone_number),
      }));
  } catch (err) {
    error.value = extractApiError(err);
  } finally {
    searching.value = false;
  }
}

async function addByIndex() {
  const index_number = normalizeIndex(quickAdd.value.indexNumber);
  if (!index_number) {
    error.value = "Enter a student index number.";
    return;
  }

  saving.value = true;
  error.value = null;
  try {
    await electionsApi.createEligibility(electionUuid.value, {
      index_number,
      phone_number: quickAdd.value.phoneNumber.trim() || undefined,
      is_eligible: eligibleForm.value.is_eligible,
      eligibility_reason: eligibleForm.value.eligibility_reason,
    });
    toast.success(toastMessages.eligibility.added);
    quickAdd.value = { indexNumber: "", phoneNumber: "" };
    await refreshRoll();
  } catch (err) {
    error.value = extractApiError(err);
  } finally {
    saving.value = false;
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
  error.value = null;
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

function openImportModal() {
  importOpen.value = true;
  importResult.value = null;
  importFile.value = null;
  error.value = null;
}

function closeImportModal() {
  importOpen.value = false;
  importFile.value = null;
  importResult.value = null;
}

function onImportFileChange(event) {
  importFile.value = event.target.files?.[0] || null;
  importResult.value = null;
}

function downloadImportTemplate() {
  const csv = [
    "index_number,phone_number,email,is_eligible,eligibility_reason",
    "BC/ITS/24/047,0247940801,,yes,Registered student voter",
    ",,student@example.com,yes,Registered student voter",
  ].join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "voter-roll-template.csv";
  link.click();
  URL.revokeObjectURL(url);
}

async function runImport() {
  if (!importFile.value) return;
  importing.value = true;
  error.value = null;
  importResult.value = null;
  try {
    const result = await electionsApi.importEligibility(electionUuid.value, importFile.value, {
      is_eligible: importForm.value.is_eligible,
      eligibility_reason: importForm.value.eligibility_reason,
    });
    importResult.value = result;
    toast.success(toastMessages.eligibility.imported(result));
    await refreshRoll();
  } catch (err) {
    error.value = extractApiError(err);
    toast.error(extractApiError(err));
  } finally {
    importing.value = false;
  }
}

onMounted(refreshRoll);
watch(() => electionUuid.value, refreshRoll);
</script>

<template>
  <ElectionWorkspacePageShell title="Eligibility" subtitle="Manage the voter roll and programme filters for this election.">
    <template #actions>
      <VButton variant="secondary" @click="openImportModal">Import CSV / Excel</VButton>
    </template>

    <VAlert v-if="error" variant="error">{{ error }}</VAlert>

    <VCard title="Add by index number">
      <p class="mb-4 text-sm text-slate-600">
        Add one student directly using their index number. Attach a phone number for OTP and SMS
        voting notifications.
      </p>
      <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
        <VInput
          v-model="quickAdd.indexNumber"
          label="Index number"
          placeholder="BC/ITS/24/047"
          @keyup.enter="addByIndex"
        />
        <VInput
          v-model="quickAdd.phoneNumber"
          label="Phone number"
          placeholder="0247940801"
          hint="Saved on the student profile when provided"
          @keyup.enter="addByIndex"
        />
      </div>
      <div class="mt-4">
        <VButton :loading="saving" @click="addByIndex">Add to voter roll</VButton>
      </div>
    </VCard>

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
        <template #cell-phone_number="{ row }">
          {{ row.phone_number || "—" }}
        </template>
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
        <template #cell-user_phone_number="{ row }">
          {{ formatPhone(row.user_phone_number) }}
        </template>
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

    <VModal v-model="importOpen" title="Import voter roll" size="md" @close="closeImportModal">
      <p class="mb-4 text-sm text-slate-600">
        Upload a CSV or Excel (.xlsx) file with student index numbers and/or emails. Each row should
        identify one voter already registered in the system.
      </p>

      <div class="mb-4 flex flex-wrap gap-2">
        <VButton size="sm" variant="ghost" type="button" @click="downloadImportTemplate">
          Download CSV template
        </VButton>
      </div>

      <div class="space-y-4">
        <div class="space-y-1.5">
          <label class="vb-label" for="eligibility-import-file">File</label>
          <input
            id="eligibility-import-file"
            type="file"
            accept=".csv,.xlsx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,text/csv"
            class="vb-input file:mr-3 file:rounded-md file:border-0 file:bg-brand-50 file:px-3 file:py-1.5 file:text-sm file:font-medium file:text-brand-700"
            @change="onImportFileChange"
          />
          <p class="text-xs text-ink-secondary">Supported formats: CSV, Excel (.xlsx)</p>
        </div>

        <VInput
          v-model="importForm.eligibility_reason"
          label="Default eligibility reason"
          placeholder="Registered student voter"
        />

        <label class="flex min-h-touch items-center gap-2 text-sm text-slate-700">
          <input
            v-model="importForm.is_eligible"
            type="checkbox"
            class="rounded border-border text-brand-600"
          />
          Mark imported voters as eligible
        </label>
      </div>

      <VAlert v-if="importResult" variant="info" class="mt-4">
        <p class="font-medium">Import summary</p>
        <ul class="mt-2 list-disc space-y-1 pl-5 text-sm">
          <li>{{ importResult.imported || 0 }} added to the roll</li>
          <li>{{ importResult.updated || 0 }} updated</li>
          <li>{{ importResult.not_found_count || 0 }} not found in the system</li>
        </ul>
        <p
          v-if="importResult.not_found?.length"
          class="mt-2 text-xs text-ink-secondary"
        >
          Not found: {{ importResult.not_found.slice(0, 8).join(", ") }}
          <span v-if="importResult.not_found.length > 8">
            (+{{ importResult.not_found.length - 8 }} more)
          </span>
        </p>
      </VAlert>

      <template #footer>
        <div class="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
          <VButton variant="secondary" type="button" :disabled="importing" @click="closeImportModal">
            Close
          </VButton>
          <VButton type="button" :loading="importing" :disabled="!importFile" @click="runImport">
            Import voters
          </VButton>
        </div>
      </template>
    </VModal>
  </ElectionWorkspacePageShell>
</template>
