<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { filterNavByRole } from "@/config/moduleNav";

const props = defineProps({
  items: {
    type: Array,
    required: true,
  },
  ariaLabel: {
    type: String,
    default: "Module navigation",
  },
});

const route = useRoute();
const authStore = useAuthStore();

const visibleItems = computed(() => filterNavByRole(props.items, authStore.role));

function isActive(item) {
  if (item.exact) return route.path === item.to;
  return route.path === item.to || route.path.startsWith(`${item.to}/`);
}
</script>

<template>
  <nav
    class="overflow-x-auto border-b border-border bg-white"
    :aria-label="ariaLabel"
  >
    <ul class="flex min-w-max gap-1 px-1 py-2 sm:px-0">
      <li v-for="item in visibleItems" :key="item.to">
        <router-link
          :to="item.to"
          class="inline-flex min-h-touch items-center rounded-input px-3 py-2 text-sm font-medium transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-600 focus-visible:ring-offset-2"
          :class="
            isActive(item)
              ? 'bg-brand-50 text-brand-700'
              : 'text-slate-600 hover:bg-surface-muted hover:text-slate-800'
          "
        >
          {{ item.label }}
        </router-link>
      </li>
    </ul>
  </nav>
</template>
