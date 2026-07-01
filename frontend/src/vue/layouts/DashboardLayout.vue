<script setup>
import { computed } from "vue";
import { RouterView, useRoute } from "vue-router";
import AppShell from "@/components/layout/AppShell.vue";
import StudentAppShell from "@/components/layout/StudentAppShell.vue";
import { useAuthStore } from "@/stores/auth";

const route = useRoute();
const authStore = useAuthStore();
const isStudentPortal = computed(() => authStore.isStudent);
</script>

<template>
  <StudentAppShell v-if="isStudentPortal" :title="(route.meta.title || 'Dashboard')">
    <RouterView v-slot="{ Component, route: activeRoute }">
      <component :is="Component" :key="activeRoute.path" />
    </RouterView>
  </StudentAppShell>

  <AppShell v-else :title="route.meta.title || 'Dashboard'">
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
