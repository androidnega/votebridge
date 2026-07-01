<script setup>
import { useRouter } from "vue-router";
import { settingsRoutes as r } from "@/config/settingsRoutes";
import { ModuleNav, PageHeader } from "@/components/ui";
import { settingsNav } from "@/config/moduleNav";
import { getSettingsSectionPalette } from "@/config/systemControlHub";

const router = useRouter();

const links = [
  {
    title: "Institution profile",
    description: "Campus identity and election office contacts.",
    to: r.institution.profile,
    paletteKey: "institution",
  },
  {
    title: "Branding",
    description: "Logos, colours, and login panel assets.",
    to: r.institution.branding,
    paletteKey: "institution",
  },
  {
    title: "Platform defaults",
    description: "System-wide defaults for new elections.",
    to: r.advanced.platformDefaults,
    paletteKey: "platform-defaults",
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
      title="Institution"
      subtitle="Identity and branding for your university election portal."
      :breadcrumbs="[{ label: 'Settings', to: r.overview }, { label: 'Institution' }]"
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
