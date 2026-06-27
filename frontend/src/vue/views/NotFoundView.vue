<script setup>
import { VButton, VCard } from "@/components/ui";
</script>

<template>
  <div class="flex min-h-[60vh] items-center justify-center">
    <VCard class="max-w-lg text-center" title="Page not found" subtitle="The page you requested does not exist or has been moved.">
      <p class="text-sm text-slate-500">
        Check the address or return to your dashboard to continue working.
      </p>
      <div class="mt-6 flex flex-wrap justify-center gap-3">
        <VButton @click="$router.push('/')">Go to dashboard</VButton>
        <VButton variant="secondary" @click="$router.push({ name: 'auth-login' })">
          Sign in
        </VButton>
      </div>
    </VCard>
  </div>
</template>
