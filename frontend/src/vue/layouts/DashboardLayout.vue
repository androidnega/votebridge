<script setup>
import { RouterView, useRoute } from "vue-router";
import AppShell from "@/components/layout/AppShell.vue";

const route = useRoute();
</script>

<template>
  <AppShell :title="route.meta.title || 'Dashboard'">
    <template #topbar-actions>
      <slot name="topbar-actions" />
    </template>
    <RouterView />
  </AppShell>
</template>
