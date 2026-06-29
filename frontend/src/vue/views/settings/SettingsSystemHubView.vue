<script setup>
import { useRouter } from "vue-router";
import { ModuleNav, PageHeader, VCard, VButton } from "@/components/ui";
import { settingsNav } from "@/config/moduleNav";

const router = useRouter();

const sections = [
  {
    title: "Runtime configuration",
    description: "Worker processes, cache, and live runtime parameters.",
    to: "/settings/runtime",
  },
  {
    title: "Environment",
    description: "Deployment environment variables and service endpoints.",
    to: "/settings/environment",
  },
  {
    title: "Storage",
    description: "Media and document storage backends.",
    to: "/settings/storage",
  },
  {
    title: "Audit settings",
    description: "Platform audit retention and logging policies.",
    to: "/settings/audit",
  },
];
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="System configuration"
      subtitle="Advanced runtime and infrastructure settings."
      :breadcrumbs="[{ label: 'Settings', to: '/settings' }, { label: 'System configuration' }]"
    />

    <ModuleNav :items="settingsNav" />

    <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
      <VCard v-for="section in sections" :key="section.title" :title="section.title">
        <p class="text-sm text-slate-600">{{ section.description }}</p>
        <VButton class="mt-4" variant="secondary" size="sm" @click="router.push(section.to)">
          Configure
        </VButton>
      </VCard>
    </div>
  </div>
</template>
