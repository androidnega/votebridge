<script setup>
import { computed, onMounted, onUnmounted, ref } from "vue";
import { useRoute } from "vue-router";
import { EmptyState, LoadingSkeleton } from "@/components/dashboard";
import { VAlert, VButton } from "@/components/ui";
import { useNotificationsStore } from "@/stores/notifications";

const route = useRoute();
const store = useNotificationsStore();
const showArchived = ref(false);

const filterLabel = computed(() => (showArchived.value ? "Archived" : "Inbox"));

onMounted(() => {
  store.fetchNotificationCenter({ archived: showArchived.value }).catch(() => {});
  store.connectRealtime(false);
});

onUnmounted(() => {
  store.disconnectRealtime(false);
});

async function toggleArchived() {
  showArchived.value = !showArchived.value;
  await store.fetchNotificationCenter({ archived: showArchived.value }).catch(() => {});
}

async function handleMarkRead(uuid) {
  await store.markRead(uuid);
}

async function handleArchive(uuid) {
  await store.archiveNotification(uuid);
}

async function handleDelete(uuid) {
  await store.deleteNotification(uuid);
}
</script>

<template>
  <div class="space-y-8">
    <div class="flex flex-wrap items-start justify-between gap-4">
      <div>
        <h2 class="text-2xl font-bold text-slate-900">Notification center</h2>
        <p class="mt-1 text-sm text-slate-500">
          {{ filterLabel }} — {{ store.unreadCount }} unread
        </p>
      </div>
      <div class="flex flex-wrap gap-2">
        <VButton variant="secondary" size="sm" @click="toggleArchived">
          {{ showArchived ? "Show inbox" : "Show archived" }}
        </VButton>
        <VButton
          v-if="!showArchived && store.unreadCount"
          size="sm"
          :loading="store.actionLoading"
          @click="store.markAllRead()"
        >
          Mark all read
        </VButton>
      </div>
    </div>

    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>
    <LoadingSkeleton v-if="store.loading && !store.notifications.length" variant="list" :rows="5" />

    <EmptyState
      v-else-if="!store.notifications.length"
      :title="showArchived ? 'No archived notifications' : 'No notifications yet'"
      description="System events such as election updates and vote confirmations appear here."
      icon="🔔"
    />

    <ul v-else class="space-y-3">
      <li
        v-for="item in store.notifications"
        :key="item.uuid"
        class="rounded-xl bg-white p-4 shadow-sm ring-1 ring-slate-900/5 sm:p-5"
        :class="{ 'border-l-4 border-brand-600': !item.is_read }"
      >
        <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div class="min-w-0 flex-1">
            <p class="font-semibold text-slate-900">{{ item.title }}</p>
            <p class="mt-1 text-sm leading-relaxed text-slate-600">{{ item.body }}</p>
            <p class="mt-2 text-xs text-slate-500">
              {{ new Date(item.created_at).toLocaleString() }}
              <span v-if="item.category" class="ml-2 capitalize">· {{ item.category.replace(/_/g, " ") }}</span>
            </p>
          </div>
          <div class="flex flex-wrap gap-2">
            <VButton
              v-if="!item.is_read && !showArchived"
              size="sm"
              variant="secondary"
              @click="handleMarkRead(item.uuid)"
            >
              Mark read
            </VButton>
            <VButton
              v-if="!showArchived"
              size="sm"
              variant="ghost"
              @click="handleArchive(item.uuid)"
            >
              Archive
            </VButton>
            <VButton size="sm" variant="ghost" @click="handleDelete(item.uuid)">
              Delete
            </VButton>
          </div>
        </div>
      </li>
    </ul>
  </div>
</template>
