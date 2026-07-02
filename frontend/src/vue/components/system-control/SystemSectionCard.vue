<script setup>
import { computed } from "vue";
import { getSettingsSectionPalette } from "@/config/systemControlHub";
import { VIcon } from "@/components/ui";

const props = defineProps({
  sectionId: { type: String, default: "" },
  title: { type: String, required: true },
  description: { type: String, default: "" },
  icon: { type: String, default: "settings" },
  hubTo: { type: String, default: "" },
  items: { type: Array, default: () => [] },
});

const palette = computed(() => getSettingsSectionPalette(props.sectionId));

const cardStyle = computed(() => ({
  backgroundColor: palette.value.bg,
  borderColor: palette.value.border,
  "--section-hover": palette.value.hoverBg,
  "--section-accent": palette.value.accent,
}));
</script>

<template>
  <article
    class="flex h-full flex-col overflow-hidden rounded-card border shadow-card"
    :style="cardStyle"
  >
    <header class="border-b px-card pb-4 pt-card" :style="{ borderColor: palette.border }">
      <div class="flex items-start gap-3">
        <div
          class="flex h-10 w-10 shrink-0 items-center justify-center rounded-input"
          :style="{ backgroundColor: palette.iconBg, color: palette.icon }"
          aria-hidden="true"
        >
          <VIcon :name="icon" size="sm" />
        </div>
        <div class="min-w-0">
          <h3 class="text-base font-semibold text-slate-900">{{ title }}</h3>
          <p v-if="description" class="mt-1 text-sm text-slate-600">{{ description }}</p>
        </div>
      </div>
    </header>

    <ul class="flex flex-1 flex-col divide-y" :style="{ borderColor: palette.border }">
      <li v-for="item in items.slice(0, 5)" :key="item.to">
        <router-link
          :to="item.to"
          class="settings-section-link group flex min-h-touch items-start justify-between gap-3 px-card py-4 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-brand-600"
        >
          <span class="min-w-0">
            <span class="block text-sm font-medium text-slate-800 group-hover:text-slate-900">
              {{ item.label }}
            </span>
            <span v-if="item.description" class="mt-0.5 block text-xs text-slate-600">
              {{ item.description }}
            </span>
          </span>
          <VIcon
            name="chevronRight"
            size="sm"
            class="mt-0.5 shrink-0 text-slate-400 transition-transform group-hover:translate-x-0.5"
            :style="{ color: 'var(--section-accent)' }"
          />
        </router-link>
      </li>
    </ul>

    <footer
      v-if="hubTo"
      class="border-t px-card py-3"
      :style="{ borderColor: palette.border }"
    >
      <router-link
        :to="hubTo"
        class="inline-flex min-h-touch items-center gap-2 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-600 focus-visible:ring-offset-2"
        :style="{ color: palette.accent }"
      >
        Open section
        <VIcon name="chevronRight" size="sm" />
      </router-link>
    </footer>
  </article>
</template>

<style scoped>
.settings-section-link:hover {
  background-color: var(--section-hover);
}
</style>
