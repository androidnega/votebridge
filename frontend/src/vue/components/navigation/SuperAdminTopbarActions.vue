<script setup>
import { useRouter } from "vue-router";
import VIcon from "@/components/ui/VIcon.vue";

const router = useRouter();

const links = [
  { label: "Strong room", icon: "strongroom", route: "/dashboard/strongroom" },
  { label: "Certification", icon: "results", route: "/dashboard/results/certification" },
  { label: "Publication", icon: "inbox", route: "/dashboard/results/publication" },
  { label: "Operations", icon: "operations", route: "/dashboard/operations" },
  { label: "Reports", icon: "analytics", route: "/dashboard/reports" },
  { label: "Settings", icon: "settings", route: "/dashboard/settings" },
];
</script>

<template>
  <nav class="hidden items-center gap-0.5 md:flex" aria-label="Governance shortcuts">
    <button
      v-for="link in links"
      :key="link.route"
      type="button"
      class="inline-flex min-h-touch items-center gap-1.5 rounded-input px-2 text-xs font-medium text-slate-600 transition hover:bg-surface-muted hover:text-slate-900"
      :title="link.label"
      @click="router.push(link.route)"
    >
      <VIcon :name="link.icon" class="h-4 w-4 shrink-0" />
      <span class="hidden 2xl:inline">{{ link.label }}</span>
    </button>
  </nav>
</template>
