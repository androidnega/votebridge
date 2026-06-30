<script setup>
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import VIcon from "@/components/ui/VIcon.vue";
import VTooltip from "@/components/ui/VTooltip.vue";
import { dashboardPath, DASHBOARD_ROOT } from "@/config/routes";
import { getSidebarNav } from "@/config/sidebarNav";
import { useSidebar } from "@/composables/useSidebar";
import { useAuthStore } from "@/stores/auth";

const props = defineProps({
  collapsed: Boolean,
});

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const { toggleGroup, isGroupExpanded } = useSidebar();

const visibleItems = computed(() => getSidebarNav(authStore.role));

function isActive(item) {
  if (item.to === DASHBOARD_ROOT) {
    return route.path === DASHBOARD_ROOT;
  }
  if (item.to === dashboardPath("elections")) {
    return (
      route.path.startsWith(dashboardPath("elections")) ||
      route.path.startsWith("/election-management")
    );
  }
  if (item.to === dashboardPath("reports")) {
    return route.path.startsWith(dashboardPath("reports")) || route.path.startsWith(dashboardPath("analytics"));
  }
  if (item.to === dashboardPath("settings")) {
    return (
      route.path.startsWith(dashboardPath("settings")) ||
      route.path.startsWith(dashboardPath("system-control"))
    );
  }
  if (item.to === dashboardPath("strongroom")) {
    return route.path.startsWith(dashboardPath("strongroom"));
  }
  return route.path === item.to || route.path.startsWith(`${item.to}/`);
}

function isChildActive(child) {
  if (child.exact) return route.path === child.to;
  return route.path === child.to || route.path.startsWith(`${child.to}/`);
}

function visibleChildren(item) {
  if (!item.children) return [];
  return item.children;
}

function groupIsActive(item) {
  if (isActive(item)) return true;
  return visibleChildren(item).some((child) => isChildActive(child));
}

function onGroupToggle(item) {
  if (props.collapsed) return;
  toggleGroup(item.key || item.name);
}

async function handleLogout() {
  await authStore.logout();
  router.push({ name: "auth-login" });
}
</script>

<template>
  <nav class="flex flex-1 flex-col">
    <ul role="list" class="flex flex-1 flex-col gap-y-1">
      <li v-for="item in visibleItems" :key="item.name">
        <template v-if="item.children && !collapsed">
          <button
            type="button"
            class="group flex min-h-touch w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition duration-200"
            :class="
              groupIsActive(item)
                ? 'bg-slate-700/60 text-white'
                : 'text-slate-300 hover:bg-slate-700 hover:text-white'
            "
            :aria-expanded="isGroupExpanded(item.key || item.name)"
            @click="onGroupToggle(item)"
          >
            <VIcon :name="item.icon" class="h-5 w-5 shrink-0" />
            <span class="flex-1 text-left">{{ item.name }}</span>
            <VIcon
              name="chevronDown"
              class="h-4 w-4 shrink-0 transition-transform duration-200"
              :class="isGroupExpanded(item.key || item.name) ? 'rotate-180' : ''"
            />
          </button>
          <ul
            v-show="isGroupExpanded(item.key || item.name)"
            class="mt-1 space-y-0.5 border-l border-slate-700 pl-3"
            role="list"
          >
            <li v-for="child in visibleChildren(item)" :key="child.to">
              <router-link
                :to="child.to"
                class="flex min-h-touch items-center rounded-lg py-2 pl-3 pr-2 text-sm transition duration-200"
                :class="
                  isChildActive(child)
                    ? 'bg-brand-600 text-white'
                    : 'text-slate-400 hover:bg-slate-700 hover:text-white'
                "
              >
                {{ child.name }}
              </router-link>
            </li>
          </ul>
        </template>

        <template v-else>
          <VTooltip v-if="collapsed" :label="item.name" position="right">
            <router-link
              :to="item.to"
              class="group flex min-h-touch items-center justify-center rounded-lg px-2 py-2.5 text-sm font-medium transition duration-200"
              :class="
                groupIsActive(item)
                  ? 'bg-brand-600 text-white'
                  : 'text-slate-300 hover:bg-slate-700 hover:text-white'
              "
            >
              <VIcon :name="item.icon" class="h-5 w-5 shrink-0" />
            </router-link>
          </VTooltip>
          <router-link
            v-else
            :to="item.to"
            class="group flex min-h-touch items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition duration-200"
            :class="
              isActive(item)
                ? 'bg-brand-600 text-white'
                : 'text-slate-300 hover:bg-slate-700 hover:text-white'
            "
          >
            <VIcon :name="item.icon" class="h-5 w-5 shrink-0" />
            <span>{{ item.name }}</span>
          </router-link>
        </template>
      </li>
    </ul>

    <div class="mt-auto border-t border-slate-700 pt-4">
      <VTooltip v-if="collapsed" label="Sign out" position="right">
        <button
          type="button"
          class="mt-1 flex min-h-touch w-full items-center justify-center rounded-lg px-2 py-2.5 text-sm font-medium text-slate-300 transition duration-200 hover:bg-slate-700 hover:text-white"
          @click="handleLogout"
        >
          <VIcon name="logout" class="h-5 w-5 shrink-0" />
        </button>
      </VTooltip>
      <button
        v-else
        type="button"
        class="mt-1 flex min-h-touch w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-slate-300 transition duration-200 hover:bg-slate-700 hover:text-white"
        @click="handleLogout"
      >
        <VIcon name="logout" class="h-5 w-5 shrink-0" />
        <span>Sign out</span>
      </button>
    </div>
  </nav>
</template>
