<script setup>
import { computed, onMounted, watch } from "vue";
import { useRoute } from "vue-router";
import { ElectionReadinessPanel } from "@/components/elections";
import ElectionLifecycleBar from "@/components/elections/ElectionLifecycleBar.vue";
import { VAlert, VButton } from "@/components/ui";
import { useElectionStore } from "@/stores/election";

const route = useRoute();
const electionStore = useElectionStore();
const electionUuid = computed(() => route.params.uuid);
const election = computed(() => electionStore.currentElection || {});

async function loadReadiness() {
  await electionStore.fetchReadiness(electionUuid.value);
}

onMounted(async () => {
  if (!electionStore.currentElection) {
    await electionStore.fetchElection(electionUuid.value).catch(() => {});
  }
  await loadReadiness();
});

watch(electionUuid, loadReadiness);
</script>

<template>
  <div class="space-y-section">
    <VAlert v-if="electionStore.error" variant="error">{{ electionStore.error }}</VAlert>

    <div class="flex flex-wrap items-center justify-between gap-3">
      <p class="text-sm text-slate-600">
        Resolve all critical checks before scheduling and opening the election.
      </p>
      <div class="flex gap-2">
        <VButton variant="secondary" size="sm" :loading="electionStore.readinessLoading" @click="loadReadiness">
          Refresh checklist
        </VButton>
        <ElectionLifecycleBar :election="election" @updated="loadReadiness" />
      </div>
    </div>

    <ElectionReadinessPanel
      :report="electionStore.readinessReport"
      :loading="electionStore.readinessLoading"
    />
  </div>
</template>
