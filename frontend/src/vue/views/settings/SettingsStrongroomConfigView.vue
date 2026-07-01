<script setup>
import { useRouter } from "vue-router";
import { settingsRoutes as r } from "@/config/settingsRoutes";
import { ModuleNav, PageHeader } from "@/components/ui";
import { settingsNav } from "@/config/moduleNav";
import { getSettingsSectionPalette } from "@/config/systemControlHub";

const router = useRouter();

const platformPolicies = [
  {
    title: "Authentication",
    description: "MFA and step-up verification for privileged access.",
    to: r.security.authentication,
    paletteKey: "security",
  },
  {
    title: "Security policies",
    description: "Rate limits, lockouts, and vault hardening.",
    to: r.security.policies,
    paletteKey: "security",
  },
  {
    title: "Audit settings",
    description: "Retention, export rules, and audit verbosity.",
    to: r.security.audit,
    paletteKey: "operations",
  },
];

const electionSetup = [
  {
    title: "Election workspace",
    description: "Nominate committee members and set vault session duration before voting opens.",
    to: "/dashboard/elections",
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
      title="Strong room configuration"
      subtitle="Platform policies for the electoral vault. Access to the vault itself requires a closed election and approved custodians."
      :breadcrumbs="[{ label: 'Settings', to: r.overview }, { label: 'Security', to: r.security.hub }, { label: 'Strong room configuration' }]"
    />
    <ModuleNav :items="settingsNav" />

    <p class="rounded-input border border-border bg-surface-muted px-4 py-3 text-sm text-slate-600">
      This page configures policies only — it does not open the Strong Room.
    </p>

    <section aria-labelledby="platform-policies-heading">
      <h2 id="platform-policies-heading" class="text-sm font-semibold text-slate-900">Platform policies</h2>
      <p class="mt-1 text-sm text-slate-500">Apply across all elections.</p>
      <div class="mt-3 grid auto-rows-fr grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <button
          v-for="item in platformPolicies"
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

    <section aria-labelledby="election-setup-heading">
      <h2 id="election-setup-heading" class="text-sm font-semibold text-slate-900">Per election</h2>
      <p class="mt-1 text-sm text-slate-500">Configured in each election workspace before voting opens.</p>
      <div class="mt-3 grid auto-rows-fr grid-cols-1 gap-4 sm:grid-cols-2">
        <button
          v-for="item in electionSetup"
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
