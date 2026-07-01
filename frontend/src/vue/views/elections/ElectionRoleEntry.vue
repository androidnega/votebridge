<script setup>
import { computed } from "vue";
import { useAuthStore } from "@/stores/auth";
import ElectionDetailView from "@/views/elections/ElectionDetailView.vue";
import ElectionWorkspaceOverview from "@/views/elections/workspace/ElectionWorkspaceOverview.vue";
import StudentElectionDetailView from "@/views/elections/StudentElectionDetailView.vue";

const authStore = useAuthStore();
const view = computed(() => {
  if (authStore.isElectionOfficer) return ElectionWorkspaceOverview;
  if (authStore.isStudent) return StudentElectionDetailView;
  return ElectionDetailView;
});
</script>

<template>
  <component :is="view" />
</template>
