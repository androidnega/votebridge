<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { VoteSuccessCard } from "@/components/voting";
import { VAlert, VButton, VInput } from "@/components/ui";
import { useVotingStore } from "@/stores/voting";

const route = useRoute();
const router = useRouter();
const votingStore = useVotingStore();

const verifyToken = ref("");
const verification = ref(null);
const verifying = ref(false);

const electionUuid = computed(() => route.params.uuid);

const confirmation = computed(() => {
  return (
    votingStore.lastConfirmation ||
    votingStore.loadConfirmation(electionUuid.value)
  );
});

onMounted(() => {
  const loaded = votingStore.loadConfirmation(electionUuid.value);
  if (!loaded) {
    router.replace(`/dashboard/elections/${electionUuid.value}`);
  }
});

async function handleVerify() {
  if (!verifyToken.value.trim()) return;
  verifying.value = true;
  try {
    verification.value = await votingStore.verifySubmittedBallot(verifyToken.value.trim());
  } catch {
    verification.value = null;
  } finally {
    verifying.value = false;
  }
}
</script>

<template>
  <div class="mx-auto max-w-2xl space-y-6">
    <VoteSuccessCard
      v-if="confirmation"
      :confirmation="confirmation"
      :verification="verification"
      :verifying="verifying"
    />

    <VAlert v-else variant="warning" title="No confirmation found">
      Submit a ballot first, or return to the election overview.
    </VAlert>

    <section
      v-if="confirmation"
      class="rounded-xl bg-white p-6 shadow-sm ring-1 ring-slate-900/5"
    >
      <h3 class="text-lg font-semibold text-slate-900">Verify your ballot</h3>
      <p class="mt-1 text-sm text-slate-500">
        Optional: confirm your vote was recorded using your Secure Voting Token.
      </p>
      <form class="mt-4 flex flex-col gap-3 sm:flex-row sm:items-end" @submit.prevent="handleVerify">
        <div class="flex-1">
          <VInput
            v-model="verifyToken"
            label="SVT token"
            placeholder="Paste your voting token"
            autocomplete="off"
          />
        </div>
        <VButton type="submit" :loading="verifying">Verify</VButton>
      </form>
      <VAlert v-if="votingStore.error" class="mt-4" variant="error">{{ votingStore.error }}</VAlert>
    </section>

    <div class="flex flex-wrap gap-3">
      <VButton variant="secondary" @click="router.push(`/dashboard/elections/${electionUuid}`)">
        Back to election
      </VButton>
      <VButton @click="router.push('/dashboard')">Dashboard</VButton>
    </div>
  </div>
</template>
