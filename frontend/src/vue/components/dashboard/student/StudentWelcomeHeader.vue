<script setup>
defineProps({
  studentName: { type: String, required: true },
  subtitle: { type: String, default: "" },
});
</script>

<template>
  <header class="mb-6">
    <h1 class="text-2xl font-bold tracking-tight text-ink-primary sm:text-3xl">
      Welcome, {{ studentName }}
    </h1>
    <p v-if="subtitle" class="mt-1.5 text-sm text-ink-secondary sm:text-base">
      {{ subtitle }}
    </p>
  </header>
</template>
