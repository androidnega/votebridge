<script setup>
import { onMounted } from "vue";
import { notificationsApi } from "@/api/notifications";
import { EmptyState, LoadingSkeleton } from "@/components/ui";
import NotificationListItem from "@/components/notifications/NotificationListItem.vue";
import { emptyStates } from "@/config/emptyStates";
import { useNotificationsStore } from "@/stores/notifications";

const props = defineProps({
  limit: { type: Number, default: 12 },
});

const store = useNotificationsStore();
const items = ref([]);
const loading = ref(false);

async function load() {
  loading.value = true;
  try {
    const data = await notificationsApi.getNotificationCenter({ limit: props.limit });
    items.value = data.items || [];
    store.unreadCount = data.unread_count || 0;
  } catch {
    items.value = [];
  } finally {
    loading.value = false;
  }
}

async function markRead(uuid) {
  await store.markRead(uuid);
  const item = items.value.find((entry) => entry.uuid === uuid);
  if (item) item.is_read = true;
}

async function archive(uuid) {
  await store.archiveNotification(uuid);
  items.value = items.value.filter((entry) => entry.uuid !== uuid);
}

async function remove(uuid) {
  await store.deleteNotification(uuid);
  items.value = items.value.filter((entry) => entry.uuid !== uuid);
}

onMounted(() => load());

defineExpose({ load });
</script>

<template>
  <LoadingSkeleton v-if="loading && !items.length" variant="list" :rows="4" />

  <EmptyState
    v-else-if="!items.length"
    class="!border-0 !bg-transparent !py-6 !shadow-none"
    v-bind="emptyStates.notifications"
  />

  <div v-else>
    <NotificationListItem
      v-for="item in items"
      :key="item.uuid"
      :item="item"
      compact
      @mark-read="markRead"
      @archive="archive"
      @delete="remove"
    />
  </div>
</template>
