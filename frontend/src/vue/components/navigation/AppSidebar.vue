<script setup>
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import VIcon from "@/components/ui/VIcon.vue";
import VTooltip from "@/components/ui/VTooltip.vue";
import { useSidebar } from "@/composables/useSidebar";
import { useAuthStore } from "@/stores/auth";

const props = defineProps({
  collapsed: Boolean,
});

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const { toggleGroup, isGroupExpanded } = useSidebar();

const navItems = [
  { name: "Overview", to: "/", icon: "home" },
  { name: "Elections", to: "/elections", icon: "elections" },
  {
    name: "Results",
    to: "/results",
    icon: "results",
    key: "results",
    children: [
      { name: "Overview", to: "/results", exact: true },
      { name: "Certification", to: "/results/certification", roles: ["super_admin"] },
      { name: "Publication", to: "/results/publication", roles: ["super_admin"] },
      { name: "Archive", to: "/results/archive", roles: ["super_admin"] },
    ],
  },
  { name: "Strongroom", to: "/strongroom", icon: "strongroom", roles: ["admin", "super_admin"] },
  {
    name: "Communications",
    to: "/communications",
    icon: "communications",
    key: "communications",
    roles: ["admin", "super_admin"],
    children: [
      { name: "Dashboard", to: "/communications", exact: true },
      { name: "Delivery logs", to: "/communications/logs" },
      { name: "Queue monitor", to: "/communications/queue" },
      { name: "Providers", to: "/communications/providers" },
      { name: "Templates", to: "/communications/templates" },
      { name: "Test center", to: "/communications/test" },
    ],
  },
  {
    name: "USSD",
    to: "/ussd",
    icon: "ussd",
    key: "ussd",
    roles: ["admin", "super_admin"],
    children: [
      { name: "Dashboard", to: "/ussd", exact: true },
      { name: "Sessions", to: "/ussd/sessions" },
      { name: "Activity logs", to: "/ussd/logs" },
    ],
  },
  {
    name: "Operations",
    to: "/operations",
    icon: "operations",
    key: "operations",
    roles: ["admin", "super_admin"],
    children: [
      { name: "Overview", to: "/operations", exact: true },
      { name: "Live Activity", to: "/operations/activity" },
      { name: "System Health", to: "/operations/health" },
      { name: "Infrastructure", to: "/operations/infrastructure" },
      { name: "Election Monitor", to: "/operations/elections" },
      { name: "Communications", to: "/operations/communications" },
      { name: "Users & Sessions", to: "/operations/sessions" },
      { name: "Queues", to: "/operations/queues" },
      { name: "Performance", to: "/operations/performance" },
      { name: "Logs", to: "/operations/logs" },
    ],
  },
  {
    name: "System Control",
    to: "/system-control",
    icon: "settings",
    key: "system-control",
    roles: ["super_admin"],
    children: [
      { name: "Overview", to: "/system-control", exact: true },
      { name: "Institution", to: "/system-control/institution" },
      { name: "Election Policies", to: "/system-control/election-policies" },
      { name: "Authentication", to: "/system-control/authentication" },
      { name: "Providers", to: "/system-control/providers" },
      { name: "Maintenance", to: "/system-control/maintenance" },
      { name: "Feature Flags", to: "/system-control/feature-flags" },
      { name: "Backup", to: "/system-control/backup" },
      { name: "Environment", to: "/system-control/environment" },
    ],
  },
  {
    name: "Analytics",
    to: "/analytics",
    icon: "analytics",
    key: "analytics",
    roles: ["admin", "super_admin"],
    children: [
      { name: "Overview", to: "/analytics", exact: true },
      { name: "Elections", to: "/analytics/elections" },
      { name: "Participation", to: "/analytics/participation" },
      { name: "Reports", to: "/analytics/reports" },
    ],
  },
  { name: "Notifications", to: "/notifications", icon: "notifications" },
  { name: "Fraud", to: "/fraud", icon: "fraud", roles: ["admin", "super_admin"] },
  { name: "Security", to: "/security", icon: "security", roles: ["admin", "super_admin"] },
];

function filterByRole(items) {
  return items.filter((item) => !item.roles || item.roles.includes(authStore.role));
}

const visibleItems = computed(() => filterByRole(navItems));

function isActive(item) {
  if (item.to === "/") return route.path === "/";
  return route.path === item.to || route.path.startsWith(`${item.to}/`);
}

function isChildActive(child) {
  if (child.exact) return route.path === child.to;
  return route.path === child.to || route.path.startsWith(`${child.to}/`);
}

function visibleChildren(item) {
  if (!item.children) return [];
  return filterByRole(item.children);
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
      <VTooltip v-if="collapsed" label="Profile" position="right">
        <router-link
          to="/profile"
          class="flex min-h-touch items-center justify-center rounded-lg px-2 py-2.5 text-sm font-medium transition duration-200"
          :class="
            route.path === '/profile'
              ? 'bg-brand-600 text-white'
              : 'text-slate-300 hover:bg-slate-700 hover:text-white'
          "
        >
          <VIcon name="profile" class="h-5 w-5 shrink-0" />
        </router-link>
      </VTooltip>
      <router-link
        v-else
        to="/profile"
        class="flex min-h-touch items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition duration-200"
        :class="
          route.path === '/profile'
            ? 'bg-brand-600 text-white'
            : 'text-slate-300 hover:bg-slate-700 hover:text-white'
        "
      >
        <VIcon name="profile" class="h-5 w-5 shrink-0" />
        <span>Profile</span>
      </router-link>

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
