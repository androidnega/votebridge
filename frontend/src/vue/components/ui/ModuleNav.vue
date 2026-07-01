<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from "vue";
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

const navRef = ref(null);
const linkRefs = ref([]);
const indicator = ref({ left: 0, width: 0, ready: false });

const visibleItems = computed(() => filterNavByRole(props.items, authStore.role));

function setLinkRef(el, index) {
  const node = el?.$el ?? el;
  if (node) {
    linkRefs.value[index] = node;
  }
}

function matchesActivePath(routePath, activePath) {
  if (activePath === "/dashboard/settings") {
    return routePath === activePath;
  }
  return routePath === activePath || routePath.startsWith(`${activePath}/`);
}

function isActive(item) {
  const [path, queryString] = item.to.split("?");
  if (queryString) {
    if (route.path !== path) return false;
    const params = new URLSearchParams(queryString);
    for (const [key, value] of params.entries()) {
      if (route.query[key] !== value) return false;
    }
    return true;
  }
  if (item.activePathPrefix) {
    if (item.exact) {
      return route.path === item.activePathPrefix;
    }
    return matchesActivePath(route.path, item.activePathPrefix);
  }
  if (item.activePaths?.length) {
    return item.activePaths.some((activePath) => matchesActivePath(route.path, activePath));
  }
  if (item.exact) return route.path === path;
  return route.path === path || route.path.startsWith(`${path}/`);
}

async function updateIndicator() {
  await nextTick();
  const activeIndex = visibleItems.value.findIndex((item) => isActive(item));
  const el = linkRefs.value[activeIndex];
  const nav = navRef.value;

  if (!el || !nav || activeIndex < 0) {
    indicator.value = { left: 0, width: 0, ready: false };
    return;
  }

  indicator.value = {
    left: el.offsetLeft,
    width: el.offsetWidth,
    ready: true,
  };
}

watch(
  () => [route.path, route.query, visibleItems.value.length],
  () => updateIndicator(),
  { flush: "post" }
);

onMounted(() => {
  updateIndicator();
  window.addEventListener("resize", updateIndicator);
  navRef.value?.addEventListener("scroll", updateIndicator, { passive: true });
});

onUnmounted(() => {
  window.removeEventListener("resize", updateIndicator);
  navRef.value?.removeEventListener("scroll", updateIndicator);
});
</script>

<template>
  <nav
    class="overflow-hidden rounded-card border border-border bg-white shadow-card"
    :aria-label="ariaLabel"
  >
    <div
      ref="navRef"
      class="relative overflow-x-auto"
    >
      <ul class="flex min-w-max items-end gap-1 px-2 pt-1">
        <li v-for="(item, index) in visibleItems" :key="item.to">
          <router-link
            :ref="(el) => setLinkRef(el, index)"
            :to="item.to"
            class="relative inline-flex items-center whitespace-nowrap rounded-input px-3 py-2.5 text-sm font-medium transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-brand-600"
            :class="
              isActive(item)
                ? 'text-shell-accent'
                : 'text-ink-secondary hover:text-ink-primary'
            "
          >
            {{ item.label }}
          </router-link>
        </li>
      </ul>

      <span
        class="pointer-events-none absolute bottom-0 h-0.5 rounded-full bg-shell-accent transition-[left,width,opacity] duration-200 ease-out"
        :class="indicator.ready ? 'opacity-100' : 'opacity-0'"
        :style="{
          left: `${indicator.left}px`,
          width: `${indicator.width}px`,
        }"
        aria-hidden="true"
      />
    </div>
  </nav>
</template>
