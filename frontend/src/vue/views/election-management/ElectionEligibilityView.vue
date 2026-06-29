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
const records = ref([]);
const loading = ref(false);
const saving = ref(false);
const error = ref(null);

const form = ref({
  user_uuid: "",
  is_eligible: true,
  eligibility_reason: "",
});

const columns = [
  { key: "user_name", label: "Voter" },
  { key: "user_index_number", label: "Index number" },
  { key: "user_email", label: "Email" },
  { key: "is_eligible", label: "Eligible" },
];

async function loadRecords() {
  if (!selectedElection.value) return;
  loading.value = true;
  error.value = null;
  try {
    const result = await electionsApi.listEligibility(selectedElection.value);
    records.value = result.items;
  } catch (err) {
    error.value = extractApiError(err);
  } finally {
    loading.value = false;
  }
}

async function addRecord() {
  if (!selectedElection.value || !form.value.user_uuid) return;
  saving.value = true;
  error.value = null;
  try {
    await electionsApi.createEligibility(selectedElection.value, form.value);
    form.value = { user_uuid: "", is_eligible: true, eligibility_reason: "" };
    await loadRecords();
  } catch (err) {
    error.value = extractApiError(err);
  } finally {
    saving.value = false;
  }
}

watch(selectedElection, loadRecords);
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="Voter eligibility"
      subtitle="Control who may vote in each election."
      :breadcrumbs="[{ label: 'Election management', to: '/elections' }, { label: 'Eligibility' }]"
    />
    <ModuleNav :items="electionManagementNav" />
    <VAlert v-if="error" variant="error">{{ error }}</VAlert>

    <VCard>
      <ElectionPicker v-model="selectedElection" />
    </VCard>

    <VCard title="Add voter eligibility" class="max-w-2xl">
      <form class="space-y-4" @submit.prevent="addRecord">
        <VInput
          v-model="form.user_uuid"
          label="User UUID"
          required
          hint="Use the voter's account UUID from the user directory."
        />
        <VInput v-model="form.eligibility_reason" label="Reason" />
        <label class="flex items-center gap-2 text-sm text-slate-700">
          <input v-model="form.is_eligible" type="checkbox" class="rounded border-border text-brand-600" />
          Eligible to vote
        </label>
        <VButton type="submit" :loading="saving" :disabled="!selectedElection">Save eligibility</VButton>
      </form>
    </VCard>

    <VCard padding="none">
      <VTable
        :columns="columns"
        :rows="records"
        :loading="loading"
        empty-text="No eligibility records yet for this election."
      >
        <template #cell-is_eligible="{ row }">
          {{ row.is_eligible ? "Yes" : "No" }}
        </template>
      </VTable>
    </VCard>
  </div>
</template>
