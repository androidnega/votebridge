<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { CandidateCard } from "@/components/voting";
import { VAlert, VButton, VCard, VInput, VModal, VTable } from "@/components/ui";
import { useToast } from "@/composables/useToast";
import { electionsApi } from "@/api/elections";
import { extractApiError } from "@/api/helpers";

const route = useRoute();
const toast = useToast();
const electionUuid = computed(() => route.params.uuid);

const positions = ref([]);
const candidates = ref([]);
const loading = ref(false);
const saving = ref(false);
const error = ref(null);
const previewCandidate = ref(null);
const editCandidate = ref(null);
const imageFile = ref(null);

const form = ref({
  position_uuid: "",
  full_name: "",
  department: "",
  manifesto: "",
});

const columns = [
  { key: "full_name", label: "Name" },
  { key: "position_title", label: "Position" },
  { key: "status_display", label: "Status" },
  { key: "actions", label: "" },
];

const positionOptions = computed(() =>
  positions.value.map((p) => ({ value: p.uuid, label: p.title }))
);

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

async function loadData() {
  loading.value = true;
  error.value = null;
  try {
    const [positionResult, candidateResult] = await Promise.all([
      electionsApi.listPositions(electionUuid.value),
      electionsApi.listCandidates(electionUuid.value),
    ]);
    positions.value = positionResult.items;
    candidates.value = candidateResult.items;
    if (!form.value.position_uuid && positions.value.length) {
      form.value.position_uuid = positions.value[0].uuid;
    }
  } catch (err) {
    error.value = extractApiError(err);
  } finally {
    loading.value = false;
  }
}

async function addCandidate() {
  if (!form.value.position_uuid) return;
  saving.value = true;
  try {
    await electionsApi.createCandidateWithImage(electionUuid.value, form.value, imageFile.value);
    form.value = { position_uuid: positions.value[0]?.uuid || "", full_name: "", department: "", manifesto: "" };
    imageFile.value = null;
    toast.success("Candidate added.");
    await loadData();
  } catch (err) {
    error.value = extractApiError(err);
  } finally {
    saving.value = false;
  }
}

async function approve(row) {
  await electionsApi.approveCandidate(electionUuid.value, row.uuid);
  toast.success("Candidate approved.");
  await loadData();
}

async function reject(row) {
  await electionsApi.rejectCandidate(electionUuid.value, row.uuid);
  toast.success("Candidate rejected.");
  await loadData();
}

async function remove(row) {
  await electionsApi.deleteCandidate(electionUuid.value, row.uuid);
  toast.success("Candidate removed.");
  await loadData();
}

function startEdit(row) {
  editCandidate.value = { ...row };
  imageFile.value = null;
}

async function saveEdit() {
  if (!editCandidate.value) return;
  saving.value = true;
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
      imageFile.value
    );
    editCandidate.value = null;
    imageFile.value = null;
    toast.success("Candidate updated.");
    await loadData();
  } catch (err) {
    error.value = extractApiError(err);
  } finally {
    saving.value = false;
  }
}

function onImageChange(event) {
  imageFile.value = event.target.files?.[0] || null;
}

onMounted(loadData);
</script>

<template>
  <div class="space-y-section">
    <VAlert v-if="error" variant="error">{{ error }}</VAlert>

    <VCard title="Register candidate" class="max-w-2xl">
      <form class="space-y-4" @submit.prevent="addCandidate">
        <div class="space-y-1.5">
          <label class="vb-label" for="candidate-position">Position</label>
          <select id="candidate-position" v-model="form.position_uuid" class="vb-input" required>
            <option v-for="opt in positionOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
          </select>
        </div>
        <VInput v-model="form.full_name" label="Full name" required />
        <VInput v-model="form.department" label="Department" />
        <div class="space-y-1.5">
          <label class="vb-label" for="manifesto">Manifesto</label>
          <textarea id="manifesto" v-model="form.manifesto" rows="4" class="vb-input" />
        </div>
        <div class="space-y-1.5">
          <label class="vb-label" for="candidate-photo">Photo</label>
          <input id="candidate-photo" type="file" accept="image/*" class="vb-input" @change="onImageChange" />
        </div>
        <VButton type="submit" :loading="saving">Add candidate</VButton>
      </form>
    </VCard>

    <VCard padding="none">
      <VTable :columns="columns" :rows="candidates" :loading="loading" empty-text="No candidates yet.">
        <template #cell-actions="{ row }">
          <div class="flex flex-wrap gap-1">
            <VButton size="sm" variant="ghost" @click="previewCandidate = row">Preview</VButton>
            <VButton v-if="row.status === 'pending'" size="sm" variant="secondary" @click="approve(row)">Approve</VButton>
            <VButton v-if="row.status === 'pending'" size="sm" variant="danger" @click="reject(row)">Reject</VButton>
            <VButton size="sm" variant="ghost" @click="startEdit(row)">Edit</VButton>
            <VButton size="sm" variant="ghost" @click="remove(row)">Remove</VButton>
          </div>
        </template>
      </VTable>
    </VCard>

    <VModal v-model="previewOpen" title="Candidate profile" size="md">
      <CandidateCard v-if="previewCandidate" :candidate="previewCandidate" disabled :tab-index="-1" />
    </VModal>

    <VModal v-model="editOpen" title="Edit candidate" size="lg">
      <form v-if="editCandidate" class="space-y-4" @submit.prevent="saveEdit">
        <VInput v-model="editCandidate.full_name" label="Full name" required />
        <VInput v-model="editCandidate.department" label="Department" />
        <div class="space-y-1.5">
          <label class="vb-label">Manifesto</label>
          <textarea v-model="editCandidate.manifesto" rows="4" class="vb-input" />
        </div>
        <input type="file" accept="image/*" class="vb-input" @change="onImageChange" />
        <VButton type="submit" :loading="saving">Save changes</VButton>
      </form>
    </VModal>
  </div>
</template>
