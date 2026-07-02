<script setup>
import { useRouter } from "vue-router";
import { settingsRoutes as r } from "@/config/settingsRoutes";
import { ModuleNav, PageHeader } from "@/components/ui";
import { settingsNav } from "@/config/moduleNav";
import { getSettingsSectionPalette } from "@/config/systemControlHub";

const router = useRouter();

const vaultPolicies = [
  {
    title: "Authentication requirements",
    description: "Step-up verification and MFA for vault custodians.",
    to: r.security.authentication,
    paletteKey: "governance",
  },
  {
    title: "Security hardening",
    description: "Rate limits and lockout thresholds for privileged access.",
    to: r.security.policies,
    paletteKey: "governance",
  },
  {
    title: "Audit retention",
    description: "Vault access logging and audit export rules.",
    to: r.security.audit,
    paletteKey: "governance",
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
      title="Strong room policies"
      subtitle="Configure vault governance parameters before elections. This does not open the Strong Room."
      :breadcrumbs="[
        { label: 'Settings', to: r.overview },
        { label: 'Election Governance', to: r.governance.hub },
        { label: 'Strong room policies' },
      ]"
    />
    <ModuleNav :items="settingsNav" />

    <p class="rounded-input border border-border bg-surface-muted px-4 py-3 text-sm text-slate-600">
      Committee membership and per-election vault setup are configured inside each election workspace before voting opens.
      Feature enable/disable for USSD or SMS belongs in Feature Flags, not here.
    </p>

    <section aria-labelledby="vault-policies-heading">
      <h2 id="vault-policies-heading" class="text-sm font-semibold text-slate-900">Vault governance policies</h2>
      <p class="mt-1 text-sm text-slate-500">Platform-wide rules applied to all electoral vault sessions.</p>
      <div class="mt-3 grid auto-rows-fr grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <button
          v-for="item in vaultPolicies"
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
