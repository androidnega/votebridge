<script setup>
import { useRouter } from "vue-router";
import VIcon from "@/components/ui/VIcon.vue";

const router = useRouter();

const links = [
  { label: "Results", icon: "results", route: "/dashboard/results" },
  { label: "Settings", icon: "settings", route: "/dashboard/settings" },
];
</script>

<template>
  <nav class="hidden items-center gap-0.5 md:flex" aria-label="Governance shortcuts">
    <button
      v-for="link in links"
      :key="link.route"
      type="button"
      class="inline-flex min-h-touch items-center gap-1.5 rounded-input px-2 text-xs font-medium text-ink-secondary transition duration-150 hover:bg-shell-sidebar-hover hover:text-shell-accent"
      :title="link.label"
      @click="router.push(link.route)"
    >
      <VIcon :name="link.icon" class="h-4 w-4 shrink-0 text-shell-sidebar-icon" />
      <span class="hidden 2xl:inline">{{ link.label }}</span>
    </button>
  </nav>
</template>
