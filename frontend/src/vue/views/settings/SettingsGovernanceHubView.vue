<script setup>
import { useRouter } from "vue-router";
import { settingsRoutes as r } from "@/config/settingsRoutes";
import { ModuleNav, PageHeader } from "@/components/ui";
import { settingsNav } from "@/config/moduleNav";
import { getSettingsSectionPalette } from "@/config/systemControlHub";

const router = useRouter();

const links = [
  {
    title: "Election administrators",
    description: "Create, suspend, and audit platform election officers.",
    to: r.governance.electionAdministration,
    paletteKey: "governance",
  },
  {
    title: "Strong room policies",
    description: "Vault committee rules, session duration, and access policies.",
    to: r.governance.strongroom,
    paletteKey: "governance",
  },
  {
    title: "Platform defaults",
    description: "System-wide defaults applied when new elections are created.",
    to: r.governance.platformDefaults,
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
      title="Election Governance"
      subtitle="Super-admin election governance — administrators, vault policy, and platform defaults."
      :breadcrumbs="[{ label: 'Settings', to: r.overview }, { label: 'Election Governance' }]"
    />
    <ModuleNav :items="settingsNav" />
    <p class="rounded-input border border-border bg-surface-muted px-4 py-3 text-sm text-slate-600">
      Day-to-day election operations — candidates, positions, and ballots — belong in the Elections workspace, not here.
    </p>
    <div class="grid auto-rows-fr grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
      <button
        v-for="item in links"
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
  </div>
</template>
