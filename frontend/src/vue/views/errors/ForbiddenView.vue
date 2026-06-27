<script setup>
import { VButton, VCard } from "@/components/ui";
</script>

<template>
  <div class="flex min-h-[60vh] items-center justify-center">
    <VCard
      class="max-w-lg text-center"
      title="Access denied"
      subtitle="You do not have permission to view this page."
    >
      <p class="text-sm text-slate-500">
        If you believe this is an error, contact your election administrator.
      </p>
      <div class="mt-6">
        <VButton @click="$router.push('/')">Return to dashboard</VButton>
      </div>
    </VCard>
  </div>
</template>
