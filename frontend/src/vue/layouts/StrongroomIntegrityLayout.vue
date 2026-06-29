<script setup>
import { ModuleNav } from "@/components/ui";
import { strongRoomIntegrityNav } from "@/config/moduleNav";
</script>

<template>
  <div class="space-y-section">
    <ModuleNav :items="strongRoomIntegrityNav" aria-label="Election integrity" />
    <RouterView />
  </div>
</template>
