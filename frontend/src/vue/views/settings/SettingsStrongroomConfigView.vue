<script setup>
import { useRouter } from "vue-router";
import { settingsNav } from "@/config/moduleNav";
import { ModuleNav, PageHeader, VButton, VCard } from "@/components/ui";

const router = useRouter();

const cards = [
  {
    title: "Committee members",
    description: "Custodians are nominated per election in the Election workspace before voting opens. Super Admin approves the committee.",
    to: "/dashboard/elections",
    action: "Open elections",
  },
  {
    title: "Access duration",
    description: "Default vault session duration is set when the election committee is configured (typically 1–4 hours).",
    to: "/dashboard/settings/audit",
    action: "Audit policies",
  },
  {
    title: "Credential policies",
    description: "Authentication, MFA, and step-up verification requirements for privileged access.",
    to: "/dashboard/settings/authentication",
    action: "Authentication",
  },
  {
    title: "Committee rotation",
    description: "Committee configuration locks when an election opens. New elections require fresh nominations.",
    to: "/dashboard/settings/feature-flags",
    action: "Feature flags",
  },
  {
    title: "Vault policies",
    description: "Rate limits, lockouts, and security hardening for vault-related operations.",
    to: "/dashboard/settings/security",
    action: "Security settings",
  },
  {
    title: "Audit policies",
    description: "Retention, export rules, and audit verbosity for platform and vault governance events.",
    to: "/dashboard/settings/audit",
    action: "Audit settings",
  },
];
</script>

<template>
  <div class="vb-page space-y-section">
    <PageHeader
      title="Strong room configuration"
      subtitle="Configure vault governance policies before elections. This does not open the Strong Room — access requires a closed election and approved custodians."
      :breadcrumbs="[{ label: 'Settings', to: '/dashboard/settings' }, { label: 'Strong room configuration' }]"
    />
    <ModuleNav :items="settingsNav" />

    <VCard title="Configuration only" class="border-info-200 bg-info-50">
      <p class="text-sm text-slate-700">
        The electoral vault is accessed only after an election closes, through an approved access request and
        multi-custodian authentication. Use this area to set platform policies; nominate committees from each
        election workspace.
      </p>
    </VCard>

    <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
      <VCard v-for="card in cards" :key="card.title" :title="card.title">
        <p class="text-sm text-slate-600">{{ card.description }}</p>
        <VButton class="mt-4" size="sm" variant="secondary" @click="router.push(card.to)">
          {{ card.action }}
        </VButton>
      </VCard>
    </div>
  </div>
</template>
