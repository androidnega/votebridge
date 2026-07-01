<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from "vue";
import { useRouter } from "vue-router";
import NotificationPreviewPanel from "@/components/notifications/NotificationPreviewPanel.vue";
import { VIcon } from "@/components/ui";
import { useNotificationsStore } from "@/stores/notifications";

const router = useRouter();
const store = useNotificationsStore();

const open = ref(false);
const panelRef = ref(null);
const previewRef = ref(null);

const unreadCount = computed(() => store.unreadCount || 0);

function toggle() {
  open.value = !open.value;
}

function close() {
  open.value = false;
}

async function openCenter() {
  close();
  await router.push({ name: "notifications" });
}

function onDocumentClick(event) {
  if (panelRef.value && !panelRef.value.contains(event.target)) {
    close();
  }
}

watch(open, (isOpen) => {
  if (!isOpen) return;
  previewRef.value?.load();
});

onMounted(() => {
  document.addEventListener("click", onDocumentClick);
  store.fetchNotificationCenter({ limit: 1 }).catch(() => {});
});

onUnmounted(() => {
  document.removeEventListener("click", onDocumentClick);
});
</script>

<template>
  <div ref="panelRef" class="relative">
    <button
      type="button"
      class="vb-topbar-icon-btn relative"
      :aria-expanded="open"
      aria-haspopup="dialog"
      aria-label="Notifications"
      @click.stop="toggle"
    >
      <VIcon name="notifications" class="h-[1.125rem] w-[1.125rem]" />
      <span
        v-if="unreadCount > 0"
        class="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-danger-600 ring-2 ring-white"
        :aria-label="`${unreadCount} unread notifications`"
      />
    </button>

    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0 translate-y-1"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 translate-y-1"
    >
      <div
        v-if="open"
        role="dialog"
        aria-label="Recent notifications"
        class="absolute right-0 z-50 mt-2 w-[min(24rem,calc(100vw-1.5rem))] origin-top-right overflow-hidden rounded-card border border-border bg-white shadow-card"
        @click.stop
      >
        <div class="flex items-center justify-between border-b border-border px-4 py-2.5">
          <div>
            <p class="text-sm font-semibold text-slate-900">Notifications</p>
            <p class="text-xs text-slate-500">
              {{ unreadCount ? `${unreadCount} unread` : "You're all caught up" }}
            </p>
          </div>
          <button
            type="button"
            class="text-xs font-medium text-brand-700 transition hover:text-brand-hover"
            @click="openCenter"
          >
            View all
          </button>
        </div>

        <div class="max-h-[min(24rem,70vh)] overflow-y-auto">
          <NotificationPreviewPanel ref="previewRef" :limit="12" />
        </div>

        <div class="border-t border-border bg-surface-muted/40 px-4 py-2">
          <button
            type="button"
            class="w-full text-center text-xs font-medium text-slate-600 transition hover:text-slate-900"
            @click="openCenter"
          >
            Open notification center
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>
