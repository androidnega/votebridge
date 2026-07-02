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

  if (!electionUuid.value) return base;

  const children = getElectionSidebarChildren(electionUuid.value, electionStatus.value, {
    isElectionOfficer: authStore.isElectionOfficer,
    isStudent: authStore.isStudent,
    isSuperAdmin: authStore.isSuperAdmin,
  });

  if (!children.length) return base;

  return base.map((item) => {
    if (item.key !== "election-management" && item.key !== "elections") return item;

    return {
      ...item,
      children: [
        { name: "All elections", to: dashboardPath("elections"), exact: true },
        ...children,
      ],
    };
  });
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
    return route.path.startsWith(dashboardPath("control-room"));
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

function hasActiveChild(item) {
  return visibleChildren(item).some((child) => isChildActive(child));
}

function isParentActive(item) {
  if (visibleChildren(item).length && hasActiveChild(item)) return false;
  return isActive(item);
}

function groupIsActive(item) {
  if (visibleChildren(item).length && !props.collapsed) {
    return isParentActive(item);
  }
  return isActive(item) || hasActiveChild(item);
}

function groupExpanded(item) {
  if (
    item.key === "election-management" &&
    (route.path.startsWith(dashboardPath("elections")) ||
      route.path.startsWith(dashboardPath("election-management")))
  ) {
    return true;
  }
  if (item.key === "elections" && electionUuid.value) return true;
  if (hasActiveChild(item)) return true;
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
    <ul role="list" class="flex flex-1 flex-col gap-y-2">
      <li v-for="item in visibleItems" :key="item.name" :class="collapsed ? 'flex justify-center' : ''">
        <template v-if="visibleChildren(item).length && !collapsed">
          <button
            type="button"
            class="vb-sidebar-group-btn"
            :class="[
              isParentActive(item) ? 'vb-sidebar-group-btn--active' : '',
              hasActiveChild(item) && !isParentActive(item) ? 'vb-sidebar-group-btn--child-active' : '',
            ]"
            :aria-expanded="groupExpanded(item)"
            @click="onGroupToggle(item)"
          >
            <VIcon
              :name="item.icon"
              class="vb-sidebar-icon"
              :class="isParentActive(item) ? 'vb-sidebar-icon--active' : ''"
            />
            <span class="flex-1 truncate text-left">{{ item.name }}</span>
            <VIcon
              name="chevronDown"
              class="h-4 w-4 shrink-0 text-shell-sidebar-icon transition-transform duration-200"
              :class="[
                groupExpanded(item) ? 'rotate-180' : '',
                hasActiveChild(item) ? 'text-brand-600' : '',
              ]"
            />
          </button>
          <ul
            v-show="groupExpanded(item)"
            class="vb-sidebar-subnav"
            role="list"
          >
            <li v-for="child in visibleChildren(item)" :key="child.to">
              <router-link
                :to="childLinkTo(child)"
                class="vb-sidebar-child-link"
                :class="[
                  isChildActive(child) ? 'vb-sidebar-child-link--active' : '',
                  child.disabled ? 'cursor-not-allowed opacity-50' : '',
                ]"
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
              class="vb-sidebar-link vb-sidebar-link--collapsed"
              :class="groupIsActive(item) ? 'vb-sidebar-link--active' : ''"
            >
              <VIcon
                :name="item.icon"
                class="vb-sidebar-icon"
                :class="groupIsActive(item) ? 'vb-sidebar-icon--active' : ''"
              />
            </router-link>
          </VTooltip>
          <router-link
            v-else
            :to="item.to"
            class="vb-sidebar-link"
            :class="isActive(item) ? 'vb-sidebar-link--active' : ''"
          >
            <VIcon
              :name="item.icon"
              class="vb-sidebar-icon"
              :class="isActive(item) ? 'vb-sidebar-icon--active' : ''"
            />
            <span class="truncate">{{ item.name }}</span>
          </router-link>
        </template>
      </li>
    </ul>

    <div
      class="mt-8 border-t border-shell-sidebar-border pt-5"
      :class="collapsed ? 'flex justify-center' : ''"
    >
      <VTooltip v-if="collapsed" label="Sign out" position="right">
        <button
          type="button"
          class="vb-sidebar-link vb-sidebar-link--collapsed vb-sidebar-footer-btn !justify-center"
          aria-label="Sign out"
          @click="handleLogout"
        >
          <VIcon name="logout" class="vb-sidebar-icon" />
        </button>
      </VTooltip>
      <button v-else type="button" class="vb-sidebar-footer-btn w-full" @click="handleLogout">
        <VIcon name="logout" class="vb-sidebar-icon" />
        <span>Sign out</span>
      </button>
    </div>
  </nav>
</template>
