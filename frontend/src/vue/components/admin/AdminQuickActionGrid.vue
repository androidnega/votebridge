<script setup>
import VIcon from "@/components/ui/VIcon.vue";
import { getAdminSoftPalette, adminQuickActionPaletteKeys } from "@/config/adminWorkspace";

defineProps({
  actions: { type: Array, default: () => [] },
});

defineEmits(["select"]);

const icons = {
  create: "elections",
  elections: "elections",
  monitor: "operations",
  results: "results",
  reports: "analytics",
  candidates: "profile",
  eligibility: "profile",
  export: "analytics",
};

function cardStyle(actionId) {
  const palette = getAdminSoftPalette(adminQuickActionPaletteKeys[actionId] || "neutral");
  return {
    "--tile-bg": palette.bg,
    "--tile-border": palette.border,
    "--tile-hover-bg": palette.hoverBg,
    "--tile-hover-border": palette.hoverBorder,
    "--tile-icon-bg": palette.iconBg,
    "--tile-icon": palette.icon,
  };
}
</script>

<template>
  <ul class="m-0 flex flex-wrap list-none gap-2.5 p-0">
    <li v-for="action in actions" :key="action.id" class="max-w-full">
      <button
        type="button"
        class="admin-soft-tile inline-flex min-h-touch w-max max-w-full items-center gap-3 rounded-input border px-3 py-3 text-left whitespace-nowrap transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-600 focus-visible:ring-offset-2"
        :style="cardStyle(action.id)"
        @click="$emit('select', action.route)"
      >
        <span
          class="flex h-9 w-9 shrink-0 items-center justify-center rounded-input"
          style="background-color: var(--tile-icon-bg); color: var(--tile-icon)"
          aria-hidden="true"
        >
          <VIcon :name="icons[action.id] || 'elections'" size="sm" />
        </span>
        <span class="text-sm font-medium leading-snug text-slate-800">{{ action.label }}</span>
      </button>
    </li>
  </ul>
</template>

<style scoped>
.admin-soft-tile {
  background-color: var(--tile-bg);
  border-color: var(--tile-border);
}

.admin-soft-tile:hover {
  background-color: var(--tile-hover-bg);
  border-color: var(--tile-hover-border);
}
</style>
