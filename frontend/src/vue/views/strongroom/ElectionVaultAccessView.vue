<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { LoadingSkeleton, VAlert, VButton, VCard } from "@/components/ui";
import { useAuthStore } from "@/stores/auth";
import { useStrongroomStore } from "@/stores/strongroom";

const ACCESS_REASONS = [
  { value: "court_order", label: "Court Order" },
  { value: "candidate_appeal", label: "Candidate Appeal" },
  { value: "electoral_commission_review", label: "Electoral Commission Review" },
  { value: "internal_audit", label: "Internal Audit" },
  { value: "integrity_verification", label: "Integrity Verification" },
];

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const store = useStrongroomStore();

const electionUuid = computed(() => route.params.uuid);
const reason = ref("integrity_verification");
const justification = ref("");

onMounted(() => {
  store.fetchAccessRequests(electionUuid.value).catch(() => {});
});

async function requestAccess() {
  await store.createAccessRequest(electionUuid.value, {
    reason: reason.value,
    justification: justification.value,
  });
  justification.value = "";
}

async function review(requestUuid, action) {
  await store.reviewAccessRequest(electionUuid.value, requestUuid, action);
}

async function openTerminal(requestUuid) {
  const session = await store.startVaultSession(electionUuid.value, requestUuid);
  router.push({
    name: "election-vault-terminal",
    params: { uuid: electionUuid.value, sessionUuid: session.uuid },
  });
}
</script>

<template>
  <div class="vb-page">
    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>

    <VCard title="Vault access request" subtitle="Strong room access requires an approved request and multi-custodian authentication.">
      <div class="space-y-4">
        <div>
          <label class="vb-label" for="reason">Reason for access</label>
          <select id="reason" v-model="reason" class="vb-input max-w-md">
            <option v-for="item in ACCESS_REASONS" :key="item.value" :value="item.value">
              {{ item.label }}
            </option>
          </select>
        </div>
        <div>
          <label class="vb-label" for="justification">Justification</label>
          <textarea id="justification" v-model="justification" rows="3" class="vb-input" placeholder="Document the lawful basis for vault access." />
        </div>
        <VButton v-if="authStore.isSuperAdmin" :loading="store.actionLoading" @click="requestAccess">
          Submit access request
        </VButton>
      </div>
    </VCard>

    <VCard title="Access requests" class="mt-4">
      <LoadingSkeleton v-if="store.loading" variant="list" :rows="3" />
      <ul v-else-if="store.accessRequests.length" class="divide-y divide-border">
        <li v-for="item in store.accessRequests" :key="item.uuid" class="flex flex-wrap items-center justify-between gap-3 py-3">
          <div>
            <p class="text-sm font-medium text-ink-primary">{{ item.reason_label }}</p>
            <p class="text-xs text-ink-secondary">{{ item.status }} · {{ item.requested_by }}</p>
          </div>
          <div class="flex flex-wrap gap-2">
            <VButton
              v-if="authStore.isSuperAdmin && item.status === 'pending'"
              size="sm"
              variant="secondary"
              @click="review(item.uuid, 'approve')"
            >
              Approve
            </VButton>
            <VButton
              v-if="authStore.isSuperAdmin && item.status === 'pending'"
              size="sm"
              variant="danger"
              @click="review(item.uuid, 'deny')"
            >
              Deny
            </VButton>
            <VButton
              v-if="item.status === 'approved'"
              size="sm"
              @click="openTerminal(item.uuid)"
            >
              Open secure terminal
            </VButton>
          </div>
        </li>
      </ul>
      <p v-else class="text-sm text-ink-secondary">No access requests yet.</p>
    </VCard>
  </div>
</template>
