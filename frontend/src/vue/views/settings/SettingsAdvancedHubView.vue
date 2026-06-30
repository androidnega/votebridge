<script setup>
import { useRouter } from "vue-router";
import { ModuleNav, PageHeader, VCard, VButton } from "@/components/ui";
import { settingsNav } from "@/config/moduleNav";

const router = useRouter();

const links = [
  { title: "Maintenance", description: "Schedule downtime and user messaging.", to: "/dashboard/settings/maintenance" },
  { title: "Backup & recovery", description: "Create, verify, and restore platform backups.", to: "/dashboard/settings/backup" },
  { title: "Platform defaults", description: "Timezone, OTP expiry, session timeout, retention.", to: "/dashboard/settings/platform-defaults" },
  { title: "Feature flags", description: "Toggle phased platform capabilities.", to: "/dashboard/settings/feature-flags" },
  { title: "System configuration", description: "Runtime, environment, and storage.", to: "/dashboard/settings/system" },
  { title: "License & about", description: "Version, support, and release information.", to: "/dashboard/settings/license" },
];
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="Advanced"
      subtitle="Platform operations for technical administrators."
      :breadcrumbs="[{ label: 'Settings', to: '/dashboard/settings' }, { label: 'Advanced' }]"
    />
    <ModuleNav :items="settingsNav" />
    <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
      <VCard v-for="item in links" :key="item.to" :title="item.title">
        <p class="text-sm text-slate-600">{{ item.description }}</p>
        <VButton class="mt-4" size="sm" variant="secondary" @click="router.push(item.to)">Open</VButton>
      </VCard>
    </div>
  </div>
</template>
