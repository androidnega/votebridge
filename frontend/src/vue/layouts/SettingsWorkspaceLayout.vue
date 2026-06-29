<script setup>
import { ModuleNav } from "@/components/ui";
import { settingsNav } from "@/config/moduleNav";
</script>

<template>
  <div class="space-y-section">
    <ModuleNav :items="settingsNav" aria-label="Settings navigation" />
    <RouterView />
  </div>
</template>
