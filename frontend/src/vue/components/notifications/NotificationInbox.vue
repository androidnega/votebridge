<script setup>
import { onMounted, ref } from "vue";
import { EmptyState, LoadingSkeleton, VAlert, VButton } from "@/components/ui";
import { emptyStates } from "@/config/emptyStates";
import NotificationListItem from "@/components/notifications/NotificationListItem.vue";
import { useNotificationInbox } from "@/composables/useNotificationInbox";

const props = defineProps({
  compact: { type: Boolean, default: false },
  limit: { type: Number, default: null },
  showHeader: { type: Boolean, default: true },
  showMarkAll: { type: Boolean, default: true },
  autoLoad: { type: Boolean, default: true },
});

const {
  store,
  filter,
  filters,
  isArchived,
  groupedNotifications,
  load,
  setFilter,
  markRead,
  markAllRead,
  archive,
  remove,
} = useNotificationInbox();

defineExpose({ load, store, filter });

onMounted(() => {
  if (props.autoLoad) {
    load(props.limit ? { limit: props.limit } : {});
  }
});
</script>

<template>
  <div class="space-y-3">
    <div
      v-if="showHeader"
      class="flex flex-wrap items-center justify-between gap-3"
    >
      <div
        class="inline-flex rounded-input border border-border bg-surface-muted p-0.5"
        role="tablist"
        aria-label="Notification filters"
      >
        <button
          v-for="tab in filters"
          :key="tab.id"
          type="button"
          role="tab"
          class="rounded-[0.625rem] px-3 py-1.5 text-xs font-medium transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-600"
          :class="
            filter === tab.id
              ? 'bg-white text-slate-900 shadow-sm'
              : 'text-slate-500 hover:text-slate-700'
          "
          :aria-selected="filter === tab.id"
          @click="setFilter(tab.id)"
        >
          {{ tab.label }}
          <span
            v-if="tab.id === 'unread' && store.unreadCount"
            class="ml-1.5 inline-flex min-w-[1.125rem] items-center justify-center rounded-full bg-brand-600 px-1 text-[10px] font-semibold text-white"
          >
            {{ store.unreadCount > 99 ? "99+" : store.unreadCount }}
          </span>
        </button>
      </div>

      <VButton
        v-if="showMarkAll && !isArchived && store.unreadCount"
        variant="ghost"
        size="sm"
        class="!min-h-8 !px-2 text-xs"
        :loading="store.actionLoading"
        @click="markAllRead()"
      >
        Mark all read
      </VButton>
    </div>

    <VAlert v-if="store.error" variant="error" class="!py-2 text-sm">{{ store.error }}</VAlert>

    <LoadingSkeleton
      v-if="store.loading && !store.notifications.length"
      variant="list"
      :rows="compact ? 4 : 6"
    />

    <EmptyState
      v-else-if="!store.notifications.length"
      class="!py-8"
      v-bind="isArchived ? emptyStates.notificationsArchived : emptyStates.notifications"
    />

    <div
      v-else
      class="overflow-hidden rounded-card border border-border bg-white shadow-card"
    >
      <section
        v-for="group in groupedNotifications"
        :key="group.label"
        :aria-label="group.label"
      >
        <h3
          v-if="!compact"
          class="border-b border-border bg-surface-muted/60 px-4 py-1.5 text-[11px] font-semibold uppercase tracking-wide text-slate-500"
        >
          {{ group.label }}
        </h3>
        <NotificationListItem
          v-for="item in group.items"
          :key="item.uuid"
          :item="item"
          :compact="compact"
          :archived="isArchived"
          @mark-read="markRead"
          @archive="archive"
          @delete="remove"
        />
      </section>
    </div>
  </div>
</template>
