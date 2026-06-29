<script setup>
import { computed } from "vue";
import { ModuleNav } from "@/components/ui";
import { filterNavByRole, strongRoomNav } from "@/config/moduleNav";
import { useAuthStore } from "@/stores/auth";

const authStore = useAuthStore();
const navItems = computed(() => filterNavByRole(strongRoomNav, authStore.role));
</script>

<template>
  <div class="space-y-section">
    <ModuleNav :items="navItems" aria-label="Strong room navigation" />
    <RouterView />
  </div>
</template>
