<script setup>
import { useRouter } from "vue-router";
import { ModuleNav, PageHeader, VCard, VButton } from "@/components/ui";
import { settingsNav } from "@/config/moduleNav";

const router = useRouter();

const links = [
  { title: "Authentication", description: "OTP, sessions, and login policies.", to: "/settings/authentication" },
  { title: "Identity configuration", description: "Biometrics and step-up verification policies.", to: "/settings/identity-assurance" },
  { title: "Security policies", description: "Rate limits, lockouts, and alert thresholds.", to: "/settings/security" },
];
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="Security"
      subtitle="Access control and identity policies for the platform."
      :breadcrumbs="[{ label: 'Settings', to: '/settings' }, { label: 'Security' }]"
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
