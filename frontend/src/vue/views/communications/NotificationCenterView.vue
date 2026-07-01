<script setup>
import { onMounted, onUnmounted } from "vue";
import NotificationInbox from "@/components/notifications/NotificationInbox.vue";
import { PageHeader } from "@/components/ui";
import { useNotificationsStore } from "@/stores/notifications";

const store = useNotificationsStore();

onMounted(() => {
  store.connectRealtime(false);
});

onUnmounted(() => {
  store.disconnectRealtime(false);
});
</script>

<template>
  <div class="vb-page space-y-section">
    <PageHeader
      title="Notifications"
      :subtitle="
        store.unreadCount
          ? `${store.unreadCount} unread message${store.unreadCount === 1 ? '' : 's'}`
          : 'You are all caught up'
      "
      :breadcrumbs="[{ label: 'Dashboard', to: '/dashboard' }, { label: 'Notifications' }]"
    />

    <NotificationInbox />
  </div>
</template>
