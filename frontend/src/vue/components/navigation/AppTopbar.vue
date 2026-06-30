<script setup>
import { computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import ConnectionStatusIndicator from "@/components/dashboard/ConnectionStatusIndicator.vue";
import GlobalSearch from "@/components/navigation/GlobalSearch.vue";
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

const router = useRouter();
const authStore = useAuthStore();
const notificationsStore = useNotificationsStore();

const unreadCount = computed(() => notificationsStore.unreadCount || 0);

const showLiveStatus = computed(() => notificationsStore.realtimeStatus === "connected");

onMounted(() => {
  notificationsStore.fetchNotificationCenter({ page_size: 1 }).catch(() => {});
});
</script>

<template>
  <header class="vb-topbar">
    <div class="flex min-w-0 items-center gap-3">
      <button
        type="button"
        class="inline-flex min-h-touch min-w-touch items-center justify-center rounded-input text-slate-500 transition hover:bg-surface-muted hover:text-slate-800"
        aria-label="Toggle sidebar"
        @click="$emit('toggle-sidebar')"
      >
        <VIcon name="panelLeft" class="h-5 w-5" />
      </button>
      <h1 class="truncate text-base font-semibold text-slate-900">{{ title }}</h1>
    </div>

    <div class="hidden min-w-0 flex-1 px-4 sm:block sm:max-w-sm md:max-w-md lg:max-w-lg">
      <GlobalSearch />
    </div>

    <div class="flex shrink-0 items-center gap-1 sm:gap-2">
      <slot name="actions" />

      <div v-if="showLiveStatus" class="hidden sm:block">
        <ConnectionStatusIndicator status="connected" />
      </div>

      <button
        type="button"
        class="relative inline-flex min-h-touch min-w-touch items-center justify-center rounded-input text-slate-500 transition hover:bg-surface-muted hover:text-slate-800"
        aria-label="Notifications"
        @click="router.push({ name: 'notifications' })"
      >
        <VIcon name="notifications" class="h-5 w-5" />
        <span
          v-if="unreadCount > 0"
          class="absolute right-1.5 top-1.5 flex h-4 min-w-[1rem] items-center justify-center rounded-full bg-danger-600 px-1 text-[10px] font-bold text-white"
        >
          {{ unreadCount > 9 ? "9+" : unreadCount }}
        </span>
      </button>

      <UserMenu compact />
    </div>
  </header>
</template>
