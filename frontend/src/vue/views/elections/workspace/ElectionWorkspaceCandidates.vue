<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { ElectionWorkspacePageShell } from "@/components/admin";
import { CandidateCard } from "@/components/voting";
import { ConfirmDialog, EmptyState, LoadingSkeleton, VAlert, VButton, VCard, VInput, VModal, VTable } from "@/components/ui";
import { emptyStates } from "@/config/emptyStates";
import { toastMessages } from "@/config/toastMessages";
import { useServerListPagination } from "@/composables/useServerListPagination";
import { useToast } from "@/composables/useToast";
import { electionsApi } from "@/api/elections";
import { extractApiError } from "@/api/helpers";

const route = useRoute();
const toast = useToast();
const electionUuid = computed(() => route.params.uuid);

const positions = ref([]);
const positionsLoading = ref(false);
const saving = ref(false);
const error = ref(null);
const addOpen = ref(false);
const previewCandidate = ref(null);
const editCandidate = ref(null);
const addImageFile = ref(null);
const editImageFile = ref(null);
const pendingAction = ref(null);

const {
  page,
  total,
  totalPages,
  rangeLabel,
  items: candidates,
  loading,
  load: loadCandidates,
  goToPage,
} = useServerListPagination(
  (params) => electionsApi.listCandidates(electionUuid.value, params),
  { pageSize: 15 }
);

const defaultForm = () => ({
  position_uuid: positions.value[0]?.uuid || "",
  full_name: "",
  department: "",
  manifesto: "",
});

const form = ref(defaultForm());

const columns = [
  { key: "full_name", label: "Name" },
  { key: "position_title", label: "Position" },
  { key: "status_display", label: "Status" },
  { key: "actions", label: "" },
];

const positionOptions = computed(() =>
  positions.value.map((p) => ({ value: p.uuid, label: p.title }))
);

const canAddCandidate = computed(() => positions.value.length > 0);

const previewOpen = computed({
  get: () => Boolean(previewCandidate.value),
  set: (value) => {
    if (!value) previewCandidate.value = null;
  },
});

const editOpen = computed({
  get: () => Boolean(editCandidate.value),
  set: (value) => {
    if (!value) editCandidate.value = null;
  },
});

const confirmOpen = computed({
  get: () => Boolean(pendingAction.value),
  set: (value) => {
    if (!value) pendingAction.value = null;
  },
});

const pageError = computed(() => error.value && !addOpen.value && !editOpen.value);

const initialLoading = computed(() => (loading.value || positionsLoading.value) && !total.value);

async function loadPositions() {
  positionsLoading.value = true;
  try {
    const result = await electionsApi.listPositions(electionUuid.value, { page_size: 100 });
    positions.value = result.items;
  } catch (err) {
    error.value = extractApiError(err);
  } finally {
    positionsLoading.value = false;
  }
}

async function refreshPage() {
  error.value = null;
  await Promise.all([loadPositions(), loadCandidates()]);
}

function openAddModal() {
  if (!canAddCandidate.value) return;
  error.value = null;
  form.value = defaultForm();
  addImageFile.value = null;
  addOpen.value = true;
}

function closeAddModal() {
  addOpen.value = false;
  form.value = defaultForm();
  addImageFile.value = null;
  error.value = null;
}

async function addCandidate() {
  if (!form.value.position_uuid || !form.value.full_name?.trim()) return;
  saving.value = true;
  error.value = null;
  try {
    await electionsApi.createCandidateWithImage(electionUuid.value, form.value, addImageFile.value);
    toast.success(toastMessages.candidate.added);
    closeAddModal();
    await refreshPage();
  } catch (err) {
    error.value = extractApiError(err);
    toast.error(extractApiError(err));
  } finally {
    saving.value = false;
  }
}

function askReject(row) {
  pendingAction.value = {
    type: "reject",
    row,
    title: "Reject candidate",
    description: `Reject ${row.full_name}? They will not appear on the ballot.`,
    confirmLabel: "Reject",
    variant: "danger",
    icon: "fraud",
  };
}

function askRemove(row) {
  pendingAction.value = {
    type: "remove",
    row,
    title: "Remove candidate",
    description: `Remove ${row.full_name} from this election? This cannot be undone.`,
    confirmLabel: "Remove",
    variant: "danger",
    icon: "fraud",
  };
}

async function runPendingAction() {
  if (!pendingAction.value) return;
  const { type, row } = pendingAction.value;
  saving.value = true;
  try {
    if (type === "reject") {
      await electionsApi.rejectCandidate(electionUuid.value, row.uuid);
      toast.success(toastMessages.candidate.rejected);
    } else if (type === "remove") {
      await electionsApi.deleteCandidate(electionUuid.value, row.uuid);
      toast.success(toastMessages.candidate.removed);
    }
    pendingAction.value = null;
    await refreshPage();
  } catch (err) {
    error.value = extractApiError(err);
    toast.error(extractApiError(err));
  } finally {
    saving.value = false;
  }
}

async function approve(row) {
  await electionsApi.approveCandidate(electionUuid.value, row.uuid);
  toast.success(toastMessages.candidate.approved);
  await refreshPage();
}

function startEdit(row) {
  editCandidate.value = { ...row };
  editImageFile.value = null;
}

function closeEditModal() {
  editCandidate.value = null;
  editImageFile.value = null;
  error.value = null;
}

async function saveEdit() {
  if (!editCandidate.value) return;
  saving.value = true;
  error.value = null;
  try {
    await electionsApi.updateCandidateWithImage(
      electionUuid.value,
      editCandidate.value.uuid,
      {
        position_uuid: editCandidate.value.position_uuid,
        full_name: editCandidate.value.full_name,
        department: editCandidate.value.department,
        manifesto: editCandidate.value.manifesto,
      },
      editImageFile.value
    );
    closeEditModal();
    toast.success(toastMessages.candidate.updated);
    await refreshPage();
  } catch (err) {
    error.value = extractApiError(err);
    toast.error(extractApiError(err));
  } finally {
    saving.value = false;
  }
}

function onAddImageChange(event) {
  addImageFile.value = event.target.files?.[0] || null;
}

function onEditImageChange(event) {
  editImageFile.value = event.target.files?.[0] || null;
}

onMounted(refreshPage);
</script>

<template>
  <ElectionWorkspacePageShell
    layout="list"
    title="Candidates"
    subtitle="Register nominees and approve them for the ballot."
  >
    <template #actions>
      <VButton :disabled="!canAddCandidate" @click="openAddModal">Add candidate</VButton>
    </template>

    <VAlert v-if="pageError" class="shrink-0" variant="error">{{ error }}</VAlert>

    <VAlert v-if="!initialLoading && !canAddCandidate" class="shrink-0" variant="warning">
      Add at least one position before registering candidates.
    </VAlert>

    <LoadingSkeleton v-if="initialLoading" class="shrink-0" variant="list" :rows="5" />

    <VCard v-else-if="total" class="vb-list-panel" padding="none">
      <VTable
        scrollable
        :columns="columns"
        :rows="candidates"
        :loading="loading"
        :page="page"
        :total-pages="totalPages"
        :total="total"
        :range-label="rangeLabel"
        @update:page="goToPage"
      >
        <template #cell-actions="{ row }">
          <div class="flex flex-wrap gap-1">
            <VButton size="sm" variant="ghost" @click="previewCandidate = row">Preview</VButton>
            <VButton v-if="row.status === 'pending'" size="sm" variant="secondary" @click="approve(row)">Approve</VButton>
            <VButton v-if="row.status === 'pending'" size="sm" variant="danger" @click="askReject(row)">Reject</VButton>
            <VButton size="sm" variant="ghost" @click="startEdit(row)">Edit</VButton>
            <VButton size="sm" variant="ghost" @click="askRemove(row)">Remove</VButton>
          </div>
        </template>
      </VTable>
    </VCard>

    <EmptyState v-else class="shrink-0" v-bind="emptyStates.candidates">
      <template #action>
        <VButton :disabled="!canAddCandidate" @click="openAddModal">Add candidate</VButton>
      </template>
    </EmptyState>

    <VModal v-model="addOpen" title="Add candidate" size="md" @close="closeAddModal">
      <VAlert v-if="error && addOpen" variant="error" class="mb-4">{{ error }}</VAlert>
      <form id="add-candidate-form" class="space-y-4" @submit.prevent="addCandidate">
        <div class="space-y-1.5">
          <label class="vb-label" for="candidate-position">Position</label>
          <select id="candidate-position" v-model="form.position_uuid" class="vb-input" required>
            <option v-for="opt in positionOptions" :key="opt.value" :value="opt.value">
              {{ opt.label }}
            </option>
          </select>
        </div>
        <VInput v-model="form.full_name" label="Full name" required />
        <VInput v-model="form.department" label="Department" placeholder="Optional" />
        <div class="space-y-1.5">
          <label class="vb-label" for="manifesto">Manifesto</label>
          <textarea
            id="manifesto"
            v-model="form.manifesto"
            rows="3"
            class="vb-input"
            placeholder="Optional — candidate statement for voters"
          />
        </div>
        <div class="space-y-1.5">
          <label class="vb-label" for="candidate-photo">Photo</label>
          <input
            id="candidate-photo"
            type="file"
            accept="image/*"
            class="vb-input file:mr-3 file:rounded-md file:border-0 file:bg-brand-50 file:px-3 file:py-1.5 file:text-sm file:font-medium file:text-brand-700"
            @change="onAddImageChange"
          />
          <p class="text-xs text-ink-secondary">Optional — JPG or PNG</p>
        </div>
      </form>

      <template #footer>
        <div class="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
          <VButton variant="secondary" type="button" :disabled="saving" @click="closeAddModal">
            Cancel
          </VButton>
          <VButton type="submit" form="add-candidate-form" :loading="saving">
            Add candidate
          </VButton>
        </div>
      </template>
    </VModal>

    <VModal v-model="previewOpen" title="Candidate profile" size="md">
      <CandidateCard v-if="previewCandidate" :candidate="previewCandidate" disabled :tab-index="-1" />
    </VModal>

    <VModal v-model="editOpen" title="Edit candidate" size="md" @close="closeEditModal">
      <VAlert v-if="error && editOpen" variant="error" class="mb-4">{{ error }}</VAlert>
      <form v-if="editCandidate" id="edit-candidate-form" class="space-y-4" @submit.prevent="saveEdit">
        <VInput v-model="editCandidate.full_name" label="Full name" required />
        <VInput v-model="editCandidate.department" label="Department" />
        <div class="space-y-1.5">
          <label class="vb-label">Manifesto</label>
          <textarea v-model="editCandidate.manifesto" rows="3" class="vb-input" />
        </div>
        <div class="space-y-1.5">
          <label class="vb-label">Replace photo</label>
          <input type="file" accept="image/*" class="vb-input" @change="onEditImageChange" />
        </div>
      </form>

      <template #footer>
        <div class="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
          <VButton variant="secondary" type="button" :disabled="saving" @click="closeEditModal">
            Cancel
          </VButton>
          <VButton type="submit" form="edit-candidate-form" :loading="saving">
            Save changes
          </VButton>
        </div>
      </template>
    </VModal>

    <ConfirmDialog
      v-model="confirmOpen"
      :title="pendingAction?.title || 'Confirm'"
      :description="pendingAction?.description || ''"
      :confirm-label="pendingAction?.confirmLabel || 'Confirm'"
      :variant="pendingAction?.variant || 'danger'"
      :icon="pendingAction?.icon || 'help'"
      :loading="saving"
      @confirm="runPendingAction"
    />
  </ElectionWorkspacePageShell>
</template>
