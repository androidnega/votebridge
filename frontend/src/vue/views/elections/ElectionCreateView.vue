<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import {
  PageHeader,
  VAlert,
  VButton,
  VCard,
  VInput,
} from "@/components/ui";
import { useElectionStore } from "@/stores/election";

const router = useRouter();
const electionStore = useElectionStore();

const form = ref({
  title: "",
  description: "",
  election_type: "general",
  start_date: "",
  end_date: "",
  allow_web_voting: true,
  allow_ussd_voting: false,
  allow_sms_notifications: false,
});

const electionTypes = [
  { value: "general", label: "General" },
  { value: "student_union", label: "Student union" },
  { value: "faculty", label: "Faculty" },
  { value: "departmental", label: "Departmental" },
  { value: "special", label: "Special" },
];

const saving = ref(false);
const localError = ref(null);

async function submit() {
  saving.value = true;
  localError.value = null;
  try {
    const election = await electionStore.createElection({
      ...form.value,
      start_date: new Date(form.value.start_date).toISOString(),
      end_date: new Date(form.value.end_date).toISOString(),
    });
    router.push({ name: "election-detail", params: { uuid: election.uuid } });
  } catch (error) {
    localError.value = electionStore.error || "Unable to create election.";
  } finally {
    saving.value = false;
  }
}
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="Create election"
      subtitle="Set up a new campus election. Positions and candidates can be added after creation."
      :breadcrumbs="[
        { label: 'Election workspace', to: '/dashboard/elections' },
        { label: 'Create' },
      ]"
    />

    <VAlert v-if="localError" variant="error">{{ localError }}</VAlert>

    <VCard class="max-w-2xl">
      <form class="space-y-4" @submit.prevent="submit">
        <VInput v-model="form.title" label="Title" required />
        <div class="space-y-1.5">
          <label class="vb-label" for="description">Description</label>
          <textarea
            id="description"
            v-model="form.description"
            rows="4"
            class="vb-input"
          />
        </div>
        <div class="space-y-1.5">
          <label class="vb-label" for="election-type">Election type</label>
          <select id="election-type" v-model="form.election_type" class="vb-input" required>
            <option v-for="type in electionTypes" :key="type.value" :value="type.value">
              {{ type.label }}
            </option>
          </select>
        </div>
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <VInput v-model="form.start_date" label="Start date" type="datetime-local" required />
          <VInput v-model="form.end_date" label="End date" type="datetime-local" required />
        </div>
        <div class="space-y-2 text-sm text-slate-700">
          <label class="flex items-center gap-2">
            <input v-model="form.allow_web_voting" type="checkbox" class="rounded border-border text-brand-600" />
            Allow web voting
          </label>
          <label class="flex items-center gap-2">
            <input v-model="form.allow_ussd_voting" type="checkbox" class="rounded border-border text-brand-600" />
            Allow USSD voting
          </label>
          <label class="flex items-center gap-2">
            <input
              v-model="form.allow_sms_notifications"
              type="checkbox"
              class="rounded border-border text-brand-600"
            />
            Allow SMS notifications
          </label>
        </div>
        <div class="flex flex-wrap gap-3">
          <VButton type="submit" :loading="saving">Create election</VButton>
          <VButton variant="secondary" type="button" @click="router.push('/dashboard/elections')">Cancel</VButton>
        </div>
      </form>
    </VCard>
  </div>
</template>
