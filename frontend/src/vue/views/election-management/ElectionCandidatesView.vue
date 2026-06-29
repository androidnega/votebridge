<script setup>
import { computed, ref, watch } from "vue";
import ElectionPicker from "@/components/elections/ElectionPicker.vue";
import {
  ModuleNav,
  PageHeader,
  VAlert,
  VButton,
  VCard,
  VInput,
  VTable,
} from "@/components/ui";
import { electionManagementNav } from "@/config/moduleNav";
import { electionsApi } from "@/api/elections";
import { extractApiError } from "@/api/helpers";

const selectedElection = ref("");
const positions = ref([]);
const candidates = ref([]);
const loading = ref(false);
const saving = ref(false);
const error = ref(null);

const form = ref({
  position_uuid: "",
  full_name: "",
  department: "",
  manifesto: "",
});

const columns = [
  { key: "full_name", label: "Name" },
  { key: "position_title", label: "Position" },
  { key: "department", label: "Department" },
  { key: "status_display", label: "Status" },
];

const positionOptions = computed(() =>
  positions.value.map((position) => ({
    value: position.uuid,
    label: position.title,
  }))
);

async function loadData() {
  if (!selectedElection.value) return;
  loading.value = true;
  error.value = null;
  try {
    const [positionResult, candidateResult] = await Promise.all([
      electionsApi.listPositions(selectedElection.value),
      electionsApi.listCandidates(selectedElection.value),
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
  if (!selectedElection.value || !form.value.position_uuid) return;
  saving.value = true;
  error.value = null;
  try {
    await electionsApi.createCandidate(selectedElection.value, form.value);
    form.value = {
      position_uuid: positions.value[0]?.uuid || "",
      full_name: "",
      department: "",
      manifesto: "",
    };
    await loadData();
  } catch (err) {
    error.value = extractApiError(err);
  } finally {
    saving.value = false;
  }
}

watch(selectedElection, loadData);
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="Candidates"
      subtitle="Register and review candidates for each election."
      :breadcrumbs="[{ label: 'Election management', to: '/elections' }, { label: 'Candidates' }]"
    />
    <ModuleNav :items="electionManagementNav" />
    <VAlert v-if="error" variant="error">{{ error }}</VAlert>

    <VCard>
      <ElectionPicker v-model="selectedElection" />
    </VCard>

    <VCard title="Add candidate" class="max-w-2xl">
      <form class="space-y-4" @submit.prevent="addCandidate">
        <div class="space-y-1.5">
          <label class="vb-label" for="candidate-position">Position</label>
          <select
            id="candidate-position"
            v-model="form.position_uuid"
            class="vb-input"
            :disabled="!positionOptions.length"
          >
            <option value="" disabled>Select a position</option>
            <option v-for="position in positionOptions" :key="position.value" :value="position.value">
              {{ position.label }}
            </option>
          </select>
        </div>
        <VInput v-model="form.full_name" label="Full name" required />
        <VInput v-model="form.department" label="Department" />
        <div class="space-y-1.5">
          <label class="vb-label" for="manifesto">Manifesto</label>
          <textarea id="manifesto" v-model="form.manifesto" rows="4" class="vb-input" />
        </div>
        <VButton type="submit" :loading="saving" :disabled="!selectedElection || !form.position_uuid">
          Add candidate
        </VButton>
      </form>
    </VCard>

    <VCard padding="none">
      <VTable
        :columns="columns"
        :rows="candidates"
        :loading="loading"
        empty-text="No candidates yet for this election."
      />
    </VCard>
  </div>
</template>
