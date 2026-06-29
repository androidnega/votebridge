<script setup>
import { ModuleNav } from "@/components/ui";

defineProps({
  navItems: {
    type: Array,
    required: true,
  },
  ariaLabel: {
    type: String,
    default: "Workspace navigation",
  },
});
</script>

<template>
  <div class="space-y-section">
    <ModuleNav :items="navItems" :aria-label="ariaLabel" />
    <RouterView />
  </div>
</template>
