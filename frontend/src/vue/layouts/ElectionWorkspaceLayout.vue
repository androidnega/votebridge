<script setup>
import { computed, onMounted, onUnmounted, watch } from "vue";
import { RouterView, useRoute } from "vue-router";
import { useElectionStore } from "@/stores/election";
import { useVotingStore } from "@/stores/voting";

const route = useRoute();
const electionStore = useElectionStore();
const votingStore = useVotingStore();

const electionUuid = computed(() => route.params.uuid);

async function loadElection() {
  if (!electionUuid.value) return;
  await electionStore.fetchElection(electionUuid.value).catch(() => {});
}

onMounted(loadElection);
watch(electionUuid, loadElection);

onUnmounted(() => {
  electionStore.clearCurrent();
  votingStore.clearBallot();
});
</script>

<template>
  <RouterView />
</template>
