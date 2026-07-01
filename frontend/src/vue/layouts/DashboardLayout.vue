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
    <RouterView v-slot="{ Component, route: activeRoute }">
      <transition
        v-if="
          activeRoute.path.startsWith('/dashboard/system-control') ||
          activeRoute.path.startsWith('/dashboard/settings') ||
          activeRoute.path.startsWith('/dashboard/reports') ||
          activeRoute.path.startsWith('/dashboard/analytics') ||
          activeRoute.path.startsWith('/dashboard/strongroom') ||
          /^\/dashboard\/elections\/[^/]+/.test(activeRoute.path)
        "
        name="vb-tab"
        mode="out-in"
      >
        <component :is="Component" :key="activeRoute.path" />
      </transition>
      <component v-else :is="Component" :key="activeRoute.path" />
    </RouterView>
  </AppShell>
</template>
