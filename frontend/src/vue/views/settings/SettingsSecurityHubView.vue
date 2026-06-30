<script setup>
import { useRouter } from "vue-router";
import { ModuleNav, PageHeader, VCard, VButton } from "@/components/ui";
import { settingsNav } from "@/config/moduleNav";

const router = useRouter();

const links = [
  { title: "Authentication", description: "OTP, sessions, and login policies.", to: "/dashboard/settings/authentication" },
  { title: "Identity assurance", description: "Biometrics and step-up verification policies.", to: "/dashboard/settings/identity-assurance" },
  { title: "Security policies", description: "Rate limits, lockouts, and alert thresholds.", to: "/dashboard/settings/security" },
  { title: "Election administration", description: "Manage Election Administrators.", to: "/dashboard/settings/election-administration" },
  { title: "Strong room configuration", description: "Vault policies before elections.", to: "/dashboard/settings/strongroom-config" },
];
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="Security"
      subtitle="Access control, identity policies, and administrator governance."
      :breadcrumbs="[{ label: 'Settings', to: '/dashboard/settings' }, { label: 'Security' }]"
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
