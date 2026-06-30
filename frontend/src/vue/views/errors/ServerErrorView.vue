<script setup>
import { VButton, VCard } from "@/components/ui";
</script>

<template>
  <div class="flex min-h-[60vh] items-center justify-center">
    <VCard
      class="max-w-lg text-center"
      title="Something went wrong"
      subtitle="An unexpected error occurred while processing your request."
    >
      <p class="text-sm text-slate-500">
        Please try again. If the problem persists, contact the election office.
      </p>
      <div class="mt-6 flex flex-wrap justify-center gap-3">
        <VButton @click="$router.go(-1)">Go back</VButton>
        <VButton variant="secondary" @click="$router.push('/dashboard')">Dashboard</VButton>
      </div>
    </VCard>
  </div>
</template>
