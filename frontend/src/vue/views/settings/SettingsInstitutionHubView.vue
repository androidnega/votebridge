<script setup>
import { useRouter } from "vue-router";
import { ModuleNav, PageHeader, VCard, VButton } from "@/components/ui";
import { settingsNav } from "@/config/moduleNav";

const router = useRouter();

const links = [
  { title: "Institution profile", description: "Campus identity and election office contacts.", to: "/dashboard/settings/institution" },
  { title: "Branding", description: "Logos, colours, and login panel assets.", to: "/dashboard/settings/branding" },
  { title: "Platform defaults", description: "System-wide defaults for new elections.", to: "/dashboard/settings/platform-defaults" },
];
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="Institution"
      subtitle="Identity and branding for your university election portal."
      :breadcrumbs="[{ label: 'Settings', to: '/dashboard/settings' }, { label: 'Institution' }]"
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
