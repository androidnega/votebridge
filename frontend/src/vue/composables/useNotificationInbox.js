import { computed, ref } from "vue";
import { groupNotificationsByDate } from "@/utils/formatTime";
import { useNotificationsStore } from "@/stores/notifications";

export function useNotificationInbox() {
  const store = useNotificationsStore();
  const filter = ref("inbox");

  const filters = [
    { id: "inbox", label: "All" },
    { id: "unread", label: "Unread" },
    { id: "archived", label: "Archived" },
  ];

  const isArchived = computed(() => filter.value === "archived");
  const isUnreadOnly = computed(() => filter.value === "unread");

  const groupedNotifications = computed(() => groupNotificationsByDate(store.notifications));

  async function load(options = {}) {
    await store.fetchNotificationCenter({
      archived: isArchived.value,
      unread: isUnreadOnly.value,
      ...options,
    });
  }

  async function setFilter(next) {
    if (filter.value === next) return;
    filter.value = next;
    await load();
  }

  async function markRead(uuid) {
    await store.markRead(uuid);
  }

  async function markAllRead() {
    await store.markAllRead();
  }

  async function archive(uuid) {
    await store.archiveNotification(uuid);
  }

  async function remove(uuid) {
    await store.deleteNotification(uuid);
  }

  return {
    store,
    filter,
    filters,
    isArchived,
    isUnreadOnly,
    groupedNotifications,
    load,
    setFilter,
    markRead,
    markAllRead,
    archive,
    remove,
  };
}
