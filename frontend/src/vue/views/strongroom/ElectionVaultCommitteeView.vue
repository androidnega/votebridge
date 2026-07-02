<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { LoadingSkeleton, VAlert, VButton, VCard } from "@/components/ui";
import { useAuthStore } from "@/stores/auth";
import { useStrongroomStore } from "@/stores/strongroom";
import { usersApi } from "@/api";

const route = useRoute();
const authStore = useAuthStore();
const store = useStrongroomStore();

const electionUuid = computed(() => route.params.uuid);
const duration = ref(2);
const selectedMembers = ref([]);
const staffOptions = ref([]);

const canEdit = computed(() => store.committee?.is_mutable && authStore.isElectionOfficer);
const canApprove = computed(
  () => store.committee?.status === "pending_approval" && authStore.isSuperAdmin
);

onMounted(async () => {
  await store.fetchCommittee(electionUuid.value).catch(() => {});
  if (store.committee) {
    duration.value = store.committee.session_duration_hours;
    selectedMembers.value = store.committee.members?.map((m) => m.user_uuid) || [];
  }
  const users = await usersApi
    .list({
      role: authStore.isSuperAdmin ? "admin,super_admin" : "admin",
      page_size: 50,
    })
    .catch(() => ({ items: [] }));
  staffOptions.value = users.items || users.results || [];
});

async function save() {
  await store.saveCommittee(electionUuid.value, {
    member_user_uuids: selectedMembers.value,
    session_duration_hours: duration.value,
  });
}

async function submit() {
  await save();
  await store.submitCommittee(electionUuid.value);
}

async function approve() {
  await store.approveCommittee(electionUuid.value);
}
</script>

<template>
  <div class="vb-page">
    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>
    <LoadingSkeleton v-if="store.loading && !store.committee" variant="card" />

    <VCard v-else title="Strong room committee" subtitle="Nominate custodians before the election opens. Configuration locks when voting begins.">
      <p v-if="store.committee" class="mb-4 text-sm text-ink-secondary">
        Status: <span class="font-semibold capitalize text-ink-primary">{{ store.committee.status.replace(/_/g, " ") }}</span>
        · Session duration: {{ store.committee.session_duration_hours }}h
      </p>

      <div v-if="canEdit" class="space-y-4">
        <div>
          <label class="vb-label" for="duration">Session duration (hours)</label>
          <select id="duration" v-model.number="duration" class="vb-input max-w-xs">
            <option :value="1">1 hour</option>
            <option :value="2">2 hours</option>
            <option :value="3">3 hours</option>
            <option :value="4">4 hours</option>
          </select>
        </div>

        <div>
          <p class="vb-label">Custodians (minimum 2)</p>
          <div class="max-h-48 space-y-2 overflow-y-auto rounded-input border border-border p-3">
            <label
              v-for="user in staffOptions"
              :key="user.uuid"
              class="flex cursor-pointer items-center gap-2 text-sm text-ink-primary"
            >
              <input v-model="selectedMembers" type="checkbox" :value="user.uuid" class="rounded border-border text-brand-600" />
              {{ user.first_name }} {{ user.last_name }} ({{ user.role?.name_display || user.role?.name }})
            </label>
          </div>
        </div>

        <div class="flex flex-wrap gap-2">
          <VButton :loading="store.actionLoading" @click="save">Save committee</VButton>
          <VButton variant="secondary" :loading="store.actionLoading" @click="submit">Submit for approval</VButton>
        </div>
      </div>

      <ul v-else-if="store.committee?.members?.length" class="space-y-2 text-sm text-ink-primary">
        <li v-for="member in store.committee.members" :key="member.uuid">
          Custodian {{ member.custodian_order }} — {{ member.full_name }}
        </li>
      </ul>

      <VButton v-if="canApprove" class="mt-4" :loading="store.actionLoading" @click="approve">
        Approve committee
      </VButton>
    </VCard>
  </div>
</template>
