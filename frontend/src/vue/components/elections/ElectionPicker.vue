<script setup>
import { onMounted, ref, watch } from "vue";
import { useElectionStore } from "@/stores/election";

const model = defineModel({ type: String, default: "" });

const electionStore = useElectionStore();
const loading = ref(false);

async function loadElections() {
  loading.value = true;
  try {
    await electionStore.fetchElections();
    if (!model.value && electionStore.elections.length) {
      model.value = electionStore.elections[0].uuid;
    }
  } catch {
    /* parent handles errors */
  } finally {
    loading.value = false;
  }
}

onMounted(loadElections);

watch(
  () => electionStore.elections.length,
  () => {
    if (!model.value && electionStore.elections.length) {
      model.value = electionStore.elections[0].uuid;
    }
  }
);
</script>

<template>
  <div class="space-y-1.5">
    <label class="vb-label" for="election-picker">Election</label>
    <select
      id="election-picker"
      v-model="model"
      class="vb-input"
      :disabled="loading || !electionStore.elections.length"
    >
      <option value="" disabled>Select an election</option>
      <option v-for="election in electionStore.elections" :key="election.uuid" :value="election.uuid">
        {{ election.title }}
      </option>
    </select>
  </div>
</template>
