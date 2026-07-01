<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { ElectionWorkspacePageShell } from "@/components/admin";
import { EmptyState, LoadingSkeleton, VAlert, VButton, VCard, VInput, VTable } from "@/components/ui";
import { emptyStates } from "@/config/emptyStates";
import { toastMessages } from "@/config/toastMessages";
import { useToast } from "@/composables/useToast";
import { electionsApi } from "@/api/elections";
import { extractApiError } from "@/api/helpers";

const route = useRoute();
const toast = useToast();
const electionUuid = computed(() => route.params.uuid);

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
  loading.value = true;
  error.value = null;
  try {
    const result = await electionsApi.listPositions(electionUuid.value);
    positions.value = result.items;
  } catch (err) {
    error.value = extractApiError(err);
  } finally {
    loading.value = false;
  }
}

async function addPosition() {
  saving.value = true;
  error.value = null;
  try {
    await electionsApi.createPosition(electionUuid.value, form.value);
    form.value = { title: "", description: "", max_votes_allowed: 1, display_order: 0, is_active: true };
    toast.success(toastMessages.position.added);
    await loadPositions();
  } catch (err) {
    error.value = extractApiError(err);
    toast.error(extractApiError(err));
  } finally {
    saving.value = false;
  }
}

onMounted(loadPositions);
</script>

<template>
  <ElectionWorkspacePageShell title="Positions" subtitle="Define offices and how many votes each voter may cast.">
    <VAlert v-if="error" variant="error">{{ error }}</VAlert>

    <VCard title="Add position" class="max-w-2xl">
      <form class="space-y-4" @submit.prevent="addPosition">
        <VInput v-model="form.title" label="Title" required />
        <div class="space-y-1.5">
          <label class="vb-label" for="position-description">Description</label>
          <textarea id="position-description" v-model="form.description" rows="3" class="vb-input" />
        </div>
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <VInput v-model.number="form.max_votes_allowed" label="Max votes allowed" type="number" min="1" required />
          <VInput v-model.number="form.display_order" label="Display order" type="number" min="0" />
        </div>
        <label class="flex min-h-touch items-center gap-2 text-sm text-slate-700">
          <input v-model="form.is_active" type="checkbox" class="rounded border-border text-brand-600" />
          Active
        </label>
        <VButton type="submit" :loading="saving">Add position</VButton>
      </form>
    </VCard>

    <LoadingSkeleton v-if="loading && !positions.length" variant="list" :rows="4" />

    <VCard v-else-if="positions.length" padding="none">
      <VTable :columns="columns" :rows="positions" :loading="loading">
        <template #cell-is_active="{ row }">{{ row.is_active ? "Yes" : "No" }}</template>
      </VTable>
    </VCard>

    <EmptyState v-else v-bind="emptyStates.positions" />
  </ElectionWorkspacePageShell>
</template>
