<script setup>
import { getAdminSoftPalette } from "@/config/adminWorkspace";

defineProps({
  title: { type: String, default: "Next required actions" },
  items: { type: Array, default: () => [] },
  emptyText: { type: String, default: "No urgent tasks — you're up to date." },
  paletteKey: { type: String, default: "tasks" },
});

const palette = getAdminSoftPalette("tasks");
</script>

<template>
  <section
    class="rounded-card border p-5 shadow-card"
    :style="{ backgroundColor: palette.bg, borderColor: palette.border }"
  >
    <h3 class="text-sm font-semibold text-slate-900">{{ title }}</h3>
    <ul v-if="items.length" class="mt-4 space-y-3">
      <li
        v-for="item in items"
        :key="item.id"
        class="rounded-input border border-white/60 bg-white/70 px-3 py-2.5"
      >
        <p class="text-sm font-medium text-slate-900">{{ item.title }}</p>
        <p v-if="item.description" class="mt-0.5 text-xs leading-relaxed text-slate-600">
          {{ item.description }}
        </p>
      </li>
    </ul>
    <p v-else class="mt-3 text-sm text-slate-600">{{ emptyText }}</p>
  </section>
</template>
