<script setup>
import { useRouter } from "vue-router";
import { ModuleNav, PageHeader, VCard, VButton } from "@/components/ui";
import { settingsNav } from "@/config/moduleNav";

const router = useRouter();

const links = [
  { title: "Integration health", description: "SMS, USSD, email, Redis, and WebSocket status.", to: "/dashboard/settings/integrations" },
  { title: "Communication providers", description: "Arkesel SMS and SMTP email configuration.", to: "/dashboard/settings/providers" },
  { title: "USSD gateway", description: "Callback URL, session limits, and gateway validation.", to: "/dashboard/settings/ussd" },
  { title: "Notifications", description: "Templates and delivery rules.", to: "/dashboard/settings/notifications" },
];
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="Integrations"
      subtitle="Communication providers and infrastructure connectivity."
      :breadcrumbs="[{ label: 'Settings', to: '/dashboard/settings' }, { label: 'Integrations' }]"
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
