<script setup>
import { useRouter } from "vue-router";
import { settingsRoutes as r } from "@/config/settingsRoutes";
import { ModuleNav, PageHeader } from "@/components/ui";
import { settingsNav } from "@/config/moduleNav";
import { getSettingsSectionPalette } from "@/config/systemControlHub";

const router = useRouter();

const links = [
  {
    title: "Feature flags",
    description: "Central place to enable or disable platform capabilities.",
    to: r.advanced.featureFlags,
    paletteKey: "advanced",
  },
  {
    title: "Environment",
    description: "Deployment context and service endpoints.",
    to: r.advanced.environment,
    paletteKey: "advanced",
  },
  {
    title: "Runtime config",
    description: "Live tunable worker and cache parameters.",
    to: r.advanced.runtime,
    paletteKey: "advanced",
  },
  {
    title: "License",
    description: "Edition and support entitlements.",
    to: r.advanced.license,
    paletteKey: "advanced",
  },
  {
    title: "About VoteBridge",
    description: "Version, release notes, and credits.",
    to: r.advanced.about,
    paletteKey: "advanced",
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
      title="Advanced"
      subtitle="Low-frequency technical settings for platform administrators."
      :breadcrumbs="[{ label: 'Settings', to: r.overview }, { label: 'Advanced' }]"
    />
    <ModuleNav :items="settingsNav" />
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
