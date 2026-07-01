<script setup>
import { useRouter } from "vue-router";
import { settingsRoutes as r } from "@/config/settingsRoutes";
import { ModuleNav, PageHeader } from "@/components/ui";
import { settingsNav } from "@/config/moduleNav";
import { getSettingsSectionPalette } from "@/config/systemControlHub";

const router = useRouter();

const accessPolicies = [
  {
    title: "Authentication",
    description: "OTP, sessions, and login policies.",
    to: r.security.authentication,
    paletteKey: "security",
  },
  {
    title: "Identity assurance",
    description: "Biometrics and step-up verification.",
    to: r.security.identityAssurance,
    paletteKey: "platform-defaults",
  },
  {
    title: "Security policies",
    description: "Rate limits, lockouts, and alert thresholds.",
    to: r.security.policies,
    paletteKey: "security",
  },
];

const governance = [
  {
    title: "Election administration",
    description: "Manage Election Administrators.",
    to: r.security.electionAdministration,
    paletteKey: "election-administration",
  },
  {
    title: "Strong room configuration",
    description: "Vault policies before elections.",
    to: r.security.strongroom,
    paletteKey: "strongroom-config",
  },
];

function cardStyle(paletteKey) {
  const palette = getSettingsSectionPalette(paletteKey);
  return { backgroundColor: palette.bg, borderColor: palette.border };
}
</script>

<template>
  <div class="vb-page space-y-section">
    <PageHeader
      title="Security"
      subtitle="Access control, identity assurance, and administrator governance."
      :breadcrumbs="[{ label: 'Settings', to: r.overview }, { label: 'Security' }]"
    />
    <ModuleNav :items="settingsNav" />

    <section aria-labelledby="access-policies-heading">
      <h2 id="access-policies-heading" class="text-sm font-semibold text-slate-900">Access & identity</h2>
      <p class="mt-1 text-sm text-slate-500">Login, verification, and platform hardening.</p>
      <div class="mt-3 grid auto-rows-fr grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <button
          v-for="item in accessPolicies"
          :key="item.to"
          type="button"
          class="flex min-h-[7.5rem] flex-col rounded-card border p-4 text-left shadow-card transition hover:brightness-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-600 focus-visible:ring-offset-2"
          :style="cardStyle(item.paletteKey)"
          @click="router.push(item.to)"
        >
          <h3 class="text-sm font-semibold text-slate-900">{{ item.title }}</h3>
          <p class="mt-2 text-xs leading-relaxed text-slate-600">{{ item.description }}</p>
        </button>
      </div>
    </section>

    <section aria-labelledby="governance-heading">
      <h2 id="governance-heading" class="text-sm font-semibold text-slate-900">Governance</h2>
      <p class="mt-1 text-sm text-slate-500">Administrators and vault policy setup.</p>
      <div class="mt-3 grid auto-rows-fr grid-cols-1 gap-4 sm:grid-cols-2">
        <button
          v-for="item in governance"
          :key="item.to"
          type="button"
          class="flex min-h-[7.5rem] flex-col rounded-card border p-4 text-left shadow-card transition hover:brightness-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-600 focus-visible:ring-offset-2"
          :style="cardStyle(item.paletteKey)"
          @click="router.push(item.to)"
        >
          <h3 class="text-sm font-semibold text-slate-900">{{ item.title }}</h3>
          <p class="mt-2 text-xs leading-relaxed text-slate-600">{{ item.description }}</p>
        </button>
      </div>
    </section>
  </div>
</template>
