<script setup>
import { computed } from "vue";
import { getSettingsSectionPalette } from "@/config/systemControlHub";

const props = defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: "" },
  paletteKey: { type: String, default: "quick-actions" },
});

const palette = computed(() => getSettingsSectionPalette(props.paletteKey));

const cardStyle = computed(() => ({
  backgroundColor: palette.value.bg,
  borderColor: palette.value.border,
  "--panel-accent": palette.value.accent,
}));
</script>

<template>
  <section
    class="overflow-hidden rounded-card border shadow-card"
    :style="cardStyle"
  >
    <header class="border-b px-card pb-4 pt-card" :style="{ borderColor: palette.border }">
      <h3 class="text-lg font-semibold text-slate-900">{{ title }}</h3>
      <p v-if="subtitle" class="mt-1 text-sm text-slate-600">{{ subtitle }}</p>
    </header>
    <div class="p-card">
      <slot />
    </div>
    <footer
      v-if="$slots.footer"
      class="border-t px-card py-4"
      :style="{ borderColor: palette.border }"
    >
      <slot name="footer" />
    </footer>
  </section>
</template>
