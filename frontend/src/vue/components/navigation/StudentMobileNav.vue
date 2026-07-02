<script setup>
import { useRoute } from "vue-router";
import VIcon from "@/components/ui/VIcon.vue";
import { studentPrimaryNav } from "@/config/studentPortalNav";

const route = useRoute();

function isActive(item) {
  if (item.key === "dashboard") return route.path === item.to;
  return route.path === item.to || route.path.startsWith(`${item.to}/`);
}
</script>

<template>
  <nav
    class="fixed inset-x-0 bottom-0 z-40 border-t border-border bg-white pb-[env(safe-area-inset-bottom)] lg:hidden"
    aria-label="Mobile navigation"
  >
    <ul class="grid grid-cols-3">
      <li v-for="item in studentPrimaryNav" :key="item.key">
        <router-link
          :to="item.to"
          class="flex min-h-[56px] flex-col items-center justify-center gap-0.5 border-t-2 px-1 text-[11px] font-medium transition"
          :class="
            isActive(item)
              ? 'border-brand-700 text-brand-700'
              : 'border-transparent text-ink-secondary'
          "
        >
          <VIcon :name="item.icon" class="h-5 w-5" />
          <span class="truncate">{{ item.name.replace("My ", "") }}</span>
        </router-link>
      </li>
    </ul>
  </nav>
</template>
