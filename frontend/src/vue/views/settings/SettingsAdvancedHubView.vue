<script setup>
import { useRouter } from "vue-router";
import { settingsRoutes as r } from "@/config/settingsRoutes";
import { ModuleNav, PageHeader } from "@/components/ui";
import { settingsNav } from "@/config/moduleNav";
import { getSettingsSectionPalette } from "@/config/systemControlHub";

const router = useRouter();

const links = [
  { title: "Maintenance", description: "Schedule downtime and user messaging.", to: r.advanced.maintenance, paletteKey: "maintenance" },
  { title: "Backup & recovery", description: "Create, verify, and restore platform backups.", to: r.advanced.backup, paletteKey: "operations" },
  { title: "Platform defaults", description: "Timezone, OTP expiry, session timeout, retention.", to: r.advanced.platformDefaults, paletteKey: "platform-defaults" },
  { title: "Feature flags", description: "Toggle phased platform capabilities.", to: r.advanced.featureFlags, paletteKey: "platform-defaults" },
  { title: "System configuration", description: "Runtime, environment, and storage.", to: r.advanced.system, paletteKey: "operations" },
  { title: "License & about", description: "Version, support, and release information.", to: r.advanced.license, paletteKey: "about" },
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
      subtitle="Platform operations for technical administrators."
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
