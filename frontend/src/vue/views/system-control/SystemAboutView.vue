<script setup>
import { settingsRoutes as r } from "@/config/settingsRoutes";
import { systemControlNav } from "@/config/moduleNav";
import { ModuleNav, PageHeader, VCard } from "@/components/ui";
import { branding } from "@/config/branding";
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="About VoteBridge"
      subtitle="Platform information and enterprise election management overview."
      :breadcrumbs="[{ label: 'Settings', to: r.overview }, { label: 'Advanced', to: r.advanced.hub }, { label: 'About' }]"
    />
    <ModuleNav :items="systemControlNav" />
    <VCard title="VoteBridge Enterprise">
      <p class="text-sm leading-relaxed text-slate-700">
        {{ branding.systemName }} is a secure campus election platform designed for institutional electoral
        commissions. The System Control Center provides Super Administrators with centralized configuration,
        policy management, and operational governance without modifying source code or environment files.
      </p>
      <p class="mt-4 text-sm text-slate-600">{{ branding.tagline }}</p>
    </VCard>
  </div>
</template>
