<script setup>
import { computed } from "vue";
import { ModuleNav, PageHeader } from "@/components/ui";
import { filterNavByRole, strongRoomNav } from "@/config/moduleNav";
import { useAuthStore } from "@/stores/auth";

const authStore = useAuthStore();
const navItems = computed(() => filterNavByRole(strongRoomNav, authStore.role));
</script>

<template>
  <div class="vb-page">
    <div class="vb-vault-shell py-4">
      <PageHeader
        title="Electoral strong room"
        subtitle="Restricted workspace for certification, custody, and integrity operations."
      />
    </div>
    <ModuleNav :items="navItems" aria-label="Strong room navigation" />
    <RouterView />
  </div>
</template>
