<script setup>
import { computed, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import VIcon from "@/components/ui/VIcon.vue";
import VTooltip from "@/components/ui/VTooltip.vue";
import { dashboardPath, DASHBOARD_ROOT } from "@/config/routes";
import { getElectionSidebarChildren } from "@/config/electionWorkspaceNav";
import { getSidebarNav } from "@/config/sidebarNav";
import { useSidebar } from "@/composables/useSidebar";
import { useAuthStore } from "@/stores/auth";
import { useElectionStore } from "@/stores/election";
import { useVotingStore } from "@/stores/voting";

const props = defineProps({
  collapsed: Boolean,
});

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const electionStore = useElectionStore();
const votingStore = useVotingStore();
const { toggleGroup, isGroupExpanded } = useSidebar();

const electionUuid = computed(() => {
  const match = route.path.match(/^\/dashboard\/elections\/([^/]+)/);
  return match?.[1] || null;
});

const electionStatus = computed(
  () => votingStore.electionStatus || electionStore.currentElection?.status || "draft"
);

const visibleItems = computed(() => {
  const base = getSidebarNav(authStore.role);
  if (authStore.isAdmin) return base;

  if (!electionUuid.value) return base;

  const children = getElectionSidebarChildren(electionUuid.value, electionStatus.value, {
    isElectionOfficer: authStore.isElectionOfficer,
    isStudent: authStore.isStudent,
    isSuperAdmin: authStore.isSuperAdmin,
  });

  if (!children.length) return base;

  return base.map((item) => (item.key === "elections" ? { ...item, children } : item));
});

watch(
  electionUuid,
  (uuid) => {
    if (!uuid) return;
    electionStore.fetchElection(uuid).catch(() => {});
  },
  { immediate: true }
);

function isActive(item) {
  if (item.to === DASHBOARD_ROOT) {
    return route.path === DASHBOARD_ROOT;
  }
  if (item.key === "election-management") {
    return (
      route.path.startsWith(dashboardPath("elections")) ||
      route.path.startsWith(dashboardPath("election-management"))
    );
  }
  if (item.key === "elections" || item.to === dashboardPath("elections")) {
    return (
      route.path.startsWith(dashboardPath("elections")) ||
      route.path.startsWith("/election-management")
    );
  }
  if (item.key === "control-room") {
    return (
      route.path.startsWith(dashboardPath("control-room")) || /\/elections\/[^/]+\/monitor$/.test(route.path)
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
  if (child.disabled) return false;
  if (child.exact) return route.path === child.to;
  return route.path === child.to || route.path.startsWith(`${child.to}/`);
}

function visibleChildren(item) {
  return item.children || [];
}

function groupIsActive(item) {
  if (isActive(item)) return true;
  return visibleChildren(item).some((child) => isChildActive(child));
}

function groupExpanded(item) {
  if (item.key === "election-management" && route.path.startsWith(dashboardPath("elections"))) return true;
  if (item.key === "elections" && electionUuid.value) return true;
  return isGroupExpanded(item.key || item.name);
}

function onGroupToggle(item) {
  if (props.collapsed) return;
  toggleGroup(item.key || item.name);
}

function childLinkTo(child) {
  if (child.disabled) return route.path;
  return child.to;
}

async function handleLogout() {
  await authStore.logout();
  router.push({ name: "auth-login" });
}
</script>

<template>
  <nav class="flex flex-1 flex-col">
    <ul role="list" class="flex flex-1 flex-col gap-y-1">
      <li v-for="item in visibleItems" :key="item.name" :class="collapsed ? 'flex justify-center' : ''">
        <template v-if="visibleChildren(item).length && !collapsed">
          <button
            type="button"
            class="group flex min-h-touch w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition duration-200"
            :class="
              groupIsActive(item)
                ? 'bg-navy-700/60 text-white'
                : 'text-slate-400 hover:bg-navy-700 hover:text-white'
            "
            :aria-expanded="groupExpanded(item)"
            @click="onGroupToggle(item)"
          >
            <VIcon :name="item.icon" class="h-5 w-5 shrink-0" />
            <span class="flex-1 truncate text-left">{{ item.name }}</span>
            <VIcon
              name="chevronDown"
              class="h-4 w-4 shrink-0 transition-transform duration-200"
              :class="groupExpanded(item) ? 'rotate-180' : ''"
            />
          </button>
          <ul
            v-show="groupExpanded(item)"
            class="mt-1 space-y-0.5 border-l border-navy-border pl-3"
            role="list"
          >
            <li v-for="child in visibleChildren(item)" :key="child.to">
              <router-link
                :to="childLinkTo(child)"
                class="flex min-h-touch items-center rounded-lg py-2 pl-3 pr-2 text-sm transition duration-200"
                :class="
                  isChildActive(child)
                    ? 'bg-brand-600 text-white'
                    : child.disabled
                      ? 'cursor-not-allowed text-slate-500 opacity-60'
                      : 'text-slate-400 hover:bg-navy-700 hover:text-white'
                "
                :aria-disabled="child.disabled ? 'true' : undefined"
              >
                <span class="truncate">{{ child.name }}</span>
              </router-link>
            </li>
          </ul>
        </template>

        <template v-else>
          <VTooltip v-if="collapsed" :label="item.name" position="right">
            <router-link
              :to="item.to"
              :aria-label="item.name"
              class="group flex h-11 w-11 items-center justify-center rounded-lg text-sm font-medium transition duration-200"
              :class="
                groupIsActive(item)
                  ? 'bg-brand-600 text-white'
                  : 'text-slate-400 hover:bg-navy-700 hover:text-white'
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
                : 'text-slate-400 hover:bg-navy-700 hover:text-white'
            "
          >
            <VIcon :name="item.icon" class="h-5 w-5 shrink-0" />
            <span class="truncate">{{ item.name }}</span>
          </router-link>
        </template>
      </li>
    </ul>

    <div class="mt-auto border-t border-navy-border pt-4" :class="collapsed ? 'flex justify-center' : ''">
      <VTooltip v-if="collapsed" label="Sign out" position="right">
        <button
          type="button"
          class="flex h-11 w-11 items-center justify-center rounded-lg text-sm font-medium text-slate-400 transition duration-200 hover:bg-navy-700 hover:text-white"
          aria-label="Sign out"
          @click="handleLogout"
        >
          <VIcon name="logout" class="h-5 w-5 shrink-0" />
        </button>
      </VTooltip>
      <button
        v-else
        type="button"
        class="mt-1 flex min-h-touch w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-slate-400 transition duration-200 hover:bg-navy-700 hover:text-white"
        @click="handleLogout"
      >
        <VIcon name="logout" class="h-5 w-5 shrink-0" />
        <span>Sign out</span>
      </button>
    </div>
  </nav>
</template>
