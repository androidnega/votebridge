<script setup>
import { ModuleNav } from "@/components/ui";
import { strongRoomInvestigationsNav } from "@/config/moduleNav";
</script>

<template>
  <div class="space-y-section">
    <ModuleNav :items="strongRoomInvestigationsNav" aria-label="Investigations" />
    <RouterView />
  </div>
</template>
