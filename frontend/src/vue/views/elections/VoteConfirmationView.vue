<script setup>
import { computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { VoteSuccessCard } from "@/components/voting";
import { VAlert, VButton } from "@/components/ui";
import { useVotingStore } from "@/stores/voting";

const route = useRoute();
const router = useRouter();
const votingStore = useVotingStore();

const electionUuid = computed(() => route.params.uuid);

const confirmation = computed(() => {
  return votingStore.lastConfirmation || votingStore.loadConfirmation(electionUuid.value);
});

onMounted(() => {
  const loaded = votingStore.loadConfirmation(electionUuid.value);
  if (!loaded) {
    router.replace(`/dashboard/elections/${electionUuid.value}`);
  }
});
</script>

<template>
  <div class="mx-auto max-w-2xl space-y-6">
    <VoteSuccessCard v-if="confirmation" :confirmation="confirmation" />

    <VAlert v-else variant="warning" title="No confirmation found">
      Submit a ballot first, or return to the election overview.
    </VAlert>

    <div class="flex flex-wrap gap-3">
      <VButton variant="secondary" @click="router.push(`/dashboard/elections/${electionUuid}`)">
        View Election
      </VButton>
      <VButton @click="router.push('/dashboard')">Return to Dashboard</VButton>
    </div>
  </div>
</template>
