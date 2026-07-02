<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { ElectionWorkspacePageShell } from "@/components/admin";
import { EmptyState, LoadingSkeleton, VAlert, VButton, VCard, VInput, VModal, VTable } from "@/components/ui";
import { emptyStates } from "@/config/emptyStates";
import { toastMessages } from "@/config/toastMessages";
import { useClientListPagination } from "@/composables/useClientListPagination";
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
const addOpen = ref(false);

const {
  page,
  total,
  totalPages,
  rangeLabel,
  items: pagedPositions,
  goToPage,
} = useClientListPagination(positions, { pageSize: 15 });

const defaultForm = () => ({
  title: "",
  description: "",
  max_votes_allowed: 1,
  display_order: 0,
  is_active: true,
});

const form = ref(defaultForm());

const columns = [
  { key: "title", label: "Title" },
  { key: "max_votes_allowed", label: "Max votes" },
  { key: "display_order", label: "Order" },
  { key: "is_active", label: "Active" },
];

function openAddModal() {
  error.value = null;
  form.value = defaultForm();
  addOpen.value = true;
}

function closeAddModal() {
  addOpen.value = false;
  form.value = defaultForm();
  error.value = null;
}

async function loadPositions() {
  loading.value = true;
  error.value = null;
  try {
    const result = await electionsApi.listPositions(electionUuid.value, { page_size: 100 });
    positions.value = result.items;
  } catch (err) {
    error.value = extractApiError(err);
  } finally {
    loading.value = false;
  }
}

async function addPosition() {
  if (!form.value.title?.trim()) return;
  saving.value = true;
  error.value = null;
  try {
    await electionsApi.createPosition(electionUuid.value, form.value);
    toast.success(toastMessages.position.added);
    closeAddModal();
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
  <ElectionWorkspacePageShell
    layout="list"
    title="Positions"
    subtitle="Define offices and how many votes each voter may cast."
  >
    <template #actions>
      <VButton @click="openAddModal">Add position</VButton>
    </template>

    <VAlert v-if="error && !addOpen" class="shrink-0" variant="error">{{ error }}</VAlert>

    <LoadingSkeleton v-if="loading && !positions.length" class="shrink-0" variant="list" :rows="4" />

    <VCard v-else-if="positions.length" class="vb-list-panel" padding="none">
      <VTable
        scrollable
        :columns="columns"
        :rows="pagedPositions"
        :loading="loading"
        :page="page"
        :total-pages="totalPages"
        :total="total"
        :range-label="rangeLabel"
        @update:page="goToPage"
      >
        <template #cell-is_active="{ row }">{{ row.is_active ? "Yes" : "No" }}</template>
      </VTable>
    </VCard>

    <EmptyState v-else class="shrink-0" v-bind="emptyStates.positions">
      <template #action>
        <VButton @click="openAddModal">Add position</VButton>
      </template>
    </EmptyState>

    <VModal v-model="addOpen" title="Add position" size="md" @close="closeAddModal">
      <VAlert v-if="error && addOpen" variant="error" class="mb-4">{{ error }}</VAlert>
      <form id="add-position-form" class="space-y-4" @submit.prevent="addPosition">
        <VInput v-model="form.title" label="Title" required />
        <div class="space-y-1.5">
          <label class="vb-label" for="position-description">Description</label>
          <textarea
            id="position-description"
            v-model="form.description"
            rows="3"
            class="vb-input"
            placeholder="Optional — shown to voters if provided"
          />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <VInput
            v-model.number="form.max_votes_allowed"
            label="Max votes allowed"
            type="number"
            min="1"
            required
          />
          <VInput v-model.number="form.display_order" label="Display order" type="number" min="0" />
        </div>
        <label class="flex min-h-touch items-center gap-2 text-sm text-slate-700">
          <input v-model="form.is_active" type="checkbox" class="rounded border-border text-brand-600" />
          Active on ballot
        </label>
      </form>

      <template #footer>
        <div class="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
          <VButton variant="secondary" type="button" :disabled="saving" @click="closeAddModal">
            Cancel
          </VButton>
          <VButton type="submit" form="add-position-form" :loading="saving">
            Add position
          </VButton>
        </div>
      </template>
    </VModal>
  </ElectionWorkspacePageShell>
</template>
