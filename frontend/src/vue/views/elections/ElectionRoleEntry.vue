<script setup>
import { computed } from "vue";
import { useAuthStore } from "@/stores/auth";
import ElectionDetailView from "@/views/elections/ElectionDetailView.vue";
import ElectionWorkspaceOverview from "@/views/elections/workspace/ElectionWorkspaceOverview.vue";

const authStore = useAuthStore();
const view = computed(() => (authStore.isAdmin ? ElectionWorkspaceOverview : ElectionDetailView));
</script>

<template>
  <component :is="view" />
</template>
