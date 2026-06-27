<script setup>
import { computed } from "vue";
import { useAuthStore } from "@/stores/auth";
import AdminDashboardView from "./AdminDashboardView.vue";
import StudentDashboardView from "./StudentDashboardView.vue";
import SuperAdminDashboardView from "./SuperAdminDashboardView.vue";

const authStore = useAuthStore();

const dashboardComponent = computed(() => {
  if (authStore.isSuperAdmin) return SuperAdminDashboardView;
  if (authStore.isAdmin) return AdminDashboardView;
  return StudentDashboardView;
});
</script>

<template>
  <component :is="dashboardComponent" />
</template>
