<script setup>
import AuthHelpFab from "@/components/auth/AuthHelpFab.vue";
import { RouterView } from "vue-router";
</script>

<template>
  <div class="vb-public-screen">
    <main class="vb-public-frame">
      <RouterView />
    </main>
    <AuthHelpFab />
  </div>
</template>
