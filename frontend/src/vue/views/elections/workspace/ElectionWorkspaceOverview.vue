<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import ElectionLifecycleBar from "@/components/elections/ElectionLifecycleBar.vue";
import { CountdownTimer, ElectionStatusBadge } from "@/components/voting";
import { LoadingSkeleton, VAlert, VButton, VCard, VInput, VModal } from "@/components/ui";
import { useToast } from "@/composables/useToast";
import { useElectionStore } from "@/stores/election";

const route = useRoute();
const router = useRouter();
const electionStore = useElectionStore();
const toast = useToast();

const electionUuid = computed(() => route.params.uuid);
const election = computed(() => electionStore.currentElection || {});

const showEdit = ref(false);
const saving = ref(false);
const editError = ref(null);

const electionTypes = [
  { value: "general", label: "General" },
  { value: "student_union", label: "Student union" },
  { value: "faculty", label: "Faculty" },
  { value: "departmental", label: "Departmental" },
  { value: "special", label: "Special" },
];

const editForm = ref({
  title: "",
  description: "",
  election_type: "general",
  start_date: "",
  end_date: "",
  allow_web_voting: true,
  allow_ussd_voting: false,
  allow_sms_notifications: false,
});

const canEdit = computed(() => ["draft", "scheduled"].includes(election.value.status));

function toLocalInput(iso) {
  if (!iso) return "";
  const date = new Date(iso);
  const pad = (value) => String(value).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

function populateEditForm() {
  editForm.value = {
    title: election.value.title || "",
    description: election.value.description || "",
    election_type: election.value.election_type || "general",
    start_date: toLocalInput(election.value.start_date),
    end_date: toLocalInput(election.value.end_date),
    allow_web_voting: election.value.allow_web_voting ?? true,
    allow_ussd_voting: election.value.allow_ussd_voting ?? false,
    allow_sms_notifications: election.value.allow_sms_notifications ?? false,
  };
}

function openEdit() {
  populateEditForm();
  editError.value = null;
  showEdit.value = true;
}

async function refresh() {
  await electionStore.fetchElection(electionUuid.value);
}

async function saveEdit() {
  saving.value = true;
  editError.value = null;
  try {
    await electionStore.updateElection(electionUuid.value, {
      ...editForm.value,
      start_date: new Date(editForm.value.start_date).toISOString(),
      end_date: new Date(editForm.value.end_date).toISOString(),
    });
    toast.success("Election updated.");
    showEdit.value = false;
    await refresh();
  } catch {
    editError.value = electionStore.error || "Unable to update election.";
  } finally {
    saving.value = false;
  }
}

watch(showEdit, (open) => {
  if (open) populateEditForm();
});

onMounted(refresh);
</script>

<template>
  <div class="space-y-section">
    <VAlert v-if="electionStore.error" variant="error">{{ electionStore.error }}</VAlert>

    <section class="overflow-hidden rounded-card bg-brand-800 p-card text-white shadow-card">
      <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div class="min-w-0 flex-1">
          <ElectionStatusBadge :status="election.status" :label="election.status_display" size="lg" />
          <h2 class="mt-3 text-2xl font-bold">{{ election.title || "Election workspace" }}</h2>
          <p v-if="election.description" class="mt-2 max-w-2xl text-sm text-brand-100">
            {{ election.description }}
          </p>
        </div>
        <div class="flex flex-col items-start gap-3 sm:items-end">
          <VButton
            v-if="canEdit"
            size="sm"
            variant="secondary"
            class="border-white/20 bg-white/10 text-white hover:bg-white/20"
            @click="openEdit"
          >
            Edit election
          </VButton>
          <CountdownTimer
            :start-date="election.start_date"
            :end-date="election.end_date"
            :status="election.status"
          />
        </div>
      </div>
      <div class="mt-4">
        <ElectionLifecycleBar :election="election" @updated="refresh" />
      </div>
    </section>

    <LoadingSkeleton v-if="electionStore.loading && !election.title" variant="card" />

    <section v-else class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <VCard title="Positions" padding="compact">
        <p class="text-2xl font-semibold text-slate-900">{{ election.position_count ?? 0 }}</p>
        <VButton class="mt-3" size="sm" variant="secondary" @click="router.push(`/elections/${electionUuid}/positions`)">
          Manage
        </VButton>
      </VCard>
      <VCard title="Candidates" padding="compact">
        <p class="text-2xl font-semibold text-slate-900">{{ election.candidate_count ?? 0 }}</p>
        <p class="text-xs text-slate-500">{{ election.approved_candidate_count ?? 0 }} approved</p>
        <VButton class="mt-3" size="sm" variant="secondary" @click="router.push(`/elections/${electionUuid}/candidates`)">
          Manage
        </VButton>
      </VCard>
      <VCard title="Eligibility" padding="compact">
        <p class="text-sm text-slate-600">Voter roll and programme filters</p>
        <VButton class="mt-3" size="sm" variant="secondary" @click="router.push(`/elections/${electionUuid}/eligibility`)">
          Manage
        </VButton>
      </VCard>
      <VCard title="Readiness" padding="compact">
        <p class="text-sm text-slate-600">Pre-open validation checklist</p>
        <VButton class="mt-3" size="sm" variant="secondary" @click="router.push(`/elections/${electionUuid}/readiness`)">
          View checklist
        </VButton>
      </VCard>
      <VCard title="Results" padding="compact">
        <p class="text-sm text-slate-600">After closing, hand over to results.</p>
        <VButton
          v-if="['closed', 'archived'].includes(election.status)"
          class="mt-3"
          size="sm"
          variant="secondary"
          @click="router.push('/results')"
        >
          View results
        </VButton>
        <VButton
          v-else-if="['open', 'paused'].includes(election.status)"
          class="mt-3"
          size="sm"
          variant="secondary"
          @click="router.push(`/elections/${electionUuid}/monitor`)"
        >
          Monitor turnout
        </VButton>
      </VCard>
    </section>

    <VModal v-model="showEdit" title="Edit election" size="lg">
      <VAlert v-if="editError" variant="error" class="mb-4">{{ editError }}</VAlert>
      <form class="space-y-4" @submit.prevent="saveEdit">
        <VInput v-model="editForm.title" label="Title" required />
        <div class="space-y-1.5">
          <label class="vb-label" for="edit-description">Description</label>
          <textarea id="edit-description" v-model="editForm.description" rows="4" class="vb-input" />
        </div>
        <div class="space-y-1.5">
          <label class="vb-label" for="edit-election-type">Election type</label>
          <select id="edit-election-type" v-model="editForm.election_type" class="vb-input" required>
            <option v-for="type in electionTypes" :key="type.value" :value="type.value">
              {{ type.label }}
            </option>
          </select>
        </div>
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <VInput v-model="editForm.start_date" label="Start date" type="datetime-local" required />
          <VInput v-model="editForm.end_date" label="End date" type="datetime-local" required />
        </div>
        <div class="space-y-2 text-sm text-slate-700">
          <label class="flex items-center gap-2">
            <input v-model="editForm.allow_web_voting" type="checkbox" class="rounded border-border text-brand-600" />
            Allow web voting
          </label>
          <label class="flex items-center gap-2">
            <input v-model="editForm.allow_ussd_voting" type="checkbox" class="rounded border-border text-brand-600" />
            Allow USSD voting
          </label>
          <label class="flex items-center gap-2">
            <input
              v-model="editForm.allow_sms_notifications"
              type="checkbox"
              class="rounded border-border text-brand-600"
            />
            Allow SMS notifications
          </label>
        </div>
        <div class="flex flex-wrap justify-end gap-3 pt-2">
          <VButton variant="secondary" type="button" @click="showEdit = false">Cancel</VButton>
          <VButton type="submit" :loading="saving">Save changes</VButton>
        </div>
      </form>
    </VModal>
  </div>
</template>
