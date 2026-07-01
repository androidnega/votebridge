<script setup>
import { computed } from "vue";
import ConnectionStatusIndicator from "@/components/dashboard/ConnectionStatusIndicator.vue";
import GlobalSearch from "@/components/navigation/GlobalSearch.vue";
import NotificationDropdown from "@/components/notifications/NotificationDropdown.vue";
import SuperAdminTopbarActions from "@/components/navigation/SuperAdminTopbarActions.vue";
import UserMenu from "@/components/navigation/UserMenu.vue";
import VIcon from "@/components/ui/VIcon.vue";
import { useAuthStore } from "@/stores/auth";
import { useNotificationsStore } from "@/stores/notifications";

defineProps({
  title: {
    type: String,
    default: "Dashboard",
  },
});

defineEmits(["toggle-sidebar"]);

const authStore = useAuthStore();
const notificationsStore = useNotificationsStore();

const showLiveStatus = computed(() => notificationsStore.realtimeStatus === "connected");
</script>

<template>
  <header class="vb-topbar">
    <div class="flex min-w-0 items-center gap-3">
      <button
        type="button"
        class="vb-topbar-icon-btn"
        aria-label="Toggle sidebar"
        @click="$emit('toggle-sidebar')"
      >
        <VIcon name="panelLeft" class="h-[1.125rem] w-[1.125rem]" />
      </button>
      <h1 class="truncate text-base font-semibold text-ink-primary">{{ title }}</h1>
      <span v-if="authStore.isSuperAdmin" class="vb-topbar-badge">Super Admin</span>
    </div>

    <div class="hidden min-w-0 flex-1 px-4 sm:block sm:max-w-sm md:max-w-md lg:max-w-lg">
      <GlobalSearch />
    </div>

    <div class="flex shrink-0 items-center gap-1 sm:gap-2">
      <slot name="actions" />

      <SuperAdminTopbarActions v-if="authStore.isSuperAdmin" />

      <div v-if="showLiveStatus" class="hidden sm:block">
        <ConnectionStatusIndicator status="connected" />
      </div>

      <NotificationDropdown />

      <UserMenu :compact="!authStore.isSuperAdmin" />
    </div>
  </header>
</template>
