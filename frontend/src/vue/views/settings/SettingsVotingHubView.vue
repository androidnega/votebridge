<script setup>
import { useRouter } from "vue-router";
import { ModuleNav, PageHeader, VCard, VButton } from "@/components/ui";
import { settingsNav } from "@/config/moduleNav";

const router = useRouter();

const links = [
  { title: "Voting channels", description: "Web, USSD, and SMS channel configuration.", to: "/dashboard/settings/voting-channels" },
  { title: "Communication providers", description: "SMS and email delivery integrations.", to: "/dashboard/settings/providers" },
  { title: "Notifications", description: "Templates and delivery rules.", to: "/dashboard/settings/notifications" },
  { title: "USSD configuration", description: "Mobile voting menu and session settings.", to: "/dashboard/settings/ussd" },
];
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="Voting"
      subtitle="Channels students use to vote and receive election messages."
      :breadcrumbs="[{ label: 'Settings', to: '/dashboard/settings' }, { label: 'Voting' }]"
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
