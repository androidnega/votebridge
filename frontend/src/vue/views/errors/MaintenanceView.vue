<script setup>
import { branding } from "@/config/branding";
import { VCard } from "@/components/ui";
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-surface-muted px-4">
    <VCard class="max-w-lg text-center" title="Scheduled maintenance" subtitle="VoteBridge is temporarily unavailable.">
      <p class="text-sm text-slate-500">
        {{ branding.institutionName }} election services are undergoing scheduled
        maintenance. Please check back shortly.
      </p>
      <p class="mt-4 text-sm text-slate-500">
        For urgent assistance, contact
        <a :href="`mailto:${branding.electionOfficeEmail}`" class="font-medium text-brand-600">
          {{ branding.electionOfficeEmail }}
        </a>
      </p>
    </VCard>
  </div>
</template>
