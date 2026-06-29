<script setup>
import { ref, watch } from "vue";
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
const loading = ref(false);
const saving = ref(false);
const error = ref(null);

const form = ref({
  title: "",
  description: "",
  max_votes_allowed: 1,
  display_order: 0,
  is_active: true,
});

const columns = [
  { key: "title", label: "Title" },
  { key: "max_votes_allowed", label: "Max votes" },
  { key: "display_order", label: "Order" },
  { key: "is_active", label: "Active" },
];

async function loadPositions() {
  if (!selectedElection.value) return;
  loading.value = true;
  error.value = null;
  try {
    const result = await electionsApi.listPositions(selectedElection.value);
    positions.value = result.items;
  } catch (err) {
    error.value = extractApiError(err);
  } finally {
    loading.value = false;
  }
}

async function addPosition() {
  if (!selectedElection.value) return;
  saving.value = true;
  error.value = null;
  try {
    await electionsApi.createPosition(selectedElection.value, form.value);
    form.value = {
      title: "",
      description: "",
      max_votes_allowed: 1,
      display_order: 0,
      is_active: true,
    };
    await loadPositions();
  } catch (err) {
    error.value = extractApiError(err);
  } finally {
    saving.value = false;
  }
}

watch(selectedElection, loadPositions);
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="Positions"
      subtitle="Define ballot positions for each election."
      :breadcrumbs="[{ label: 'Election management', to: '/elections' }, { label: 'Positions' }]"
    />
    <ModuleNav :items="electionManagementNav" />
    <VAlert v-if="error" variant="error">{{ error }}</VAlert>

    <VCard>
      <ElectionPicker v-model="selectedElection" />
    </VCard>

    <VCard title="Add position" class="max-w-2xl">
      <form class="space-y-4" @submit.prevent="addPosition">
        <VInput v-model="form.title" label="Title" required />
        <div class="space-y-1.5">
          <label class="vb-label" for="position-description">Description</label>
          <textarea id="position-description" v-model="form.description" rows="3" class="vb-input" />
        </div>
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <VInput
            v-model.number="form.max_votes_allowed"
            label="Max votes allowed"
            type="number"
            min="1"
            required
          />
          <VInput v-model.number="form.display_order" label="Display order" type="number" min="0" />
        </div>
        <label class="flex items-center gap-2 text-sm text-slate-700">
          <input v-model="form.is_active" type="checkbox" class="rounded border-border text-brand-600" />
          Active
        </label>
        <VButton type="submit" :loading="saving" :disabled="!selectedElection">Add position</VButton>
      </form>
    </VCard>

    <VCard padding="none">
      <VTable
        :columns="columns"
        :rows="positions"
        :loading="loading"
        empty-text="No positions yet for this election."
      >
        <template #cell-is_active="{ row }">
          {{ row.is_active ? "Yes" : "No" }}
        </template>
      </VTable>
    </VCard>
  </div>
</template>
