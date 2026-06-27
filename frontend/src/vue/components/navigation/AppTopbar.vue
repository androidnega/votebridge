<script setup>
import { computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import ConnectionStatusIndicator from "@/components/dashboard/ConnectionStatusIndicator.vue";
import GlobalSearch from "@/components/navigation/GlobalSearch.vue";
import UserMenu from "@/components/navigation/UserMenu.vue";
import VButton from "@/components/ui/VButton.vue";
import VIcon from "@/components/ui/VIcon.vue";
import { branding } from "@/config/branding";
import { useAuthStore } from "@/stores/auth";
import { useElectionStore } from "@/stores/election";
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
const electionStore = useElectionStore();
const notificationsStore = useNotificationsStore();

const currentElection = computed(() => {
  const open = electionStore.elections.find((e) => e.status === "open");
  return open?.title || null;
});

const unreadCount = computed(() => notificationsStore.unreadCount || 0);

onMounted(() => {
  if (!electionStore.elections.length) {
    electionStore.fetchElections().catch(() => {});
  }
  notificationsStore.fetchNotificationCenter({ page_size: 1 }).catch(() => {});
});
</script>

<template>
  <header
    class="sticky top-0 z-40 flex h-topbar shrink-0 items-center gap-3 border-b border-border bg-white px-4 shadow-sm sm:gap-4 sm:px-6 lg:px-8"
  >
    <VButton
      variant="ghost"
      size="sm"
      class="!min-h-touch !p-2"
      aria-label="Toggle sidebar"
      @click="$emit('toggle-sidebar')"
    >
      <VIcon name="panelLeft" class="h-5 w-5" />
    </VButton>

    <div class="flex min-w-0 items-center gap-3">
      <div
        class="hidden h-9 w-9 shrink-0 items-center justify-center overflow-hidden rounded-lg bg-brand-50 sm:flex"
        aria-hidden="true"
      >
        <img
          v-if="branding.institutionLogoUrl"
          :src="branding.institutionLogoUrl"
          :alt="`${branding.institutionName} logo`"
          class="h-full w-full object-contain p-1"
        />
        <span v-else class="text-xs font-bold text-brand-700">VB</span>
      </div>
      <div class="hidden min-w-0 flex-col md:flex">
        <span class="truncate text-xs font-medium uppercase tracking-wide text-slate-500">
          {{ branding.institutionName }}
        </span>
        <span class="truncate text-sm font-semibold text-slate-800">{{ title }}</span>
        <span v-if="currentElection" class="truncate text-xs text-brand-600">
          {{ currentElection }}
        </span>
      </div>
      <span class="truncate text-sm font-semibold text-slate-800 md:hidden">{{ title }}</span>
    </div>

    <div class="flex flex-1 items-center justify-end gap-2 sm:gap-3">
      <GlobalSearch />

      <slot name="actions" />

      <ConnectionStatusIndicator class="hidden lg:flex" />

      <VButton
        variant="ghost"
        size="sm"
        class="relative !min-h-touch !p-2"
        aria-label="Notifications"
        @click="router.push({ name: 'notifications' })"
      >
        <VIcon name="notifications" class="h-5 w-5" />
        <span
          v-if="unreadCount > 0"
          class="absolute right-1 top-1 flex h-4 min-w-[1rem] items-center justify-center rounded-full bg-danger-600 px-1 text-[10px] font-bold text-white"
        >
          {{ unreadCount > 9 ? "9+" : unreadCount }}
        </span>
      </VButton>

      <UserMenu />
    </div>
  </header>
</template>
