<script setup>
import EmptyState from "./EmptyState.vue";
import LoadingSkeleton from "./LoadingSkeleton.vue";

defineProps({
  title: String,
  items: {
    type: Array,
    default: () => [],
  },
  loading: Boolean,
  emptyTitle: {
    type: String,
    default: "No activity yet",
  },
  emptyDescription: {
    type: String,
    default: "Recent events will appear here.",
  },
});

function formatDate(value) {
  if (!value) return "";
  return new Date(value).toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}
</script>

<template>
  <section class="rounded-xl bg-white p-5 shadow-sm ring-1 ring-slate-900/5">
    <div v-if="title" class="mb-4 flex items-center justify-between">
      <h3 class="text-sm font-semibold text-slate-900">{{ title }}</h3>
      <span v-if="!loading" class="text-xs text-slate-500">{{ items.length }} items</span>
    </div>

    <LoadingSkeleton v-if="loading" variant="list" :rows="4" />

    <EmptyState
      v-else-if="items.length === 0"
      :title="emptyTitle"
      :description="emptyDescription"
    />

    <ul v-else class="max-h-80 space-y-3 overflow-y-auto">
      <li
        v-for="(item, index) in items"
        :key="item.id || item.alert_id || item.fraud_case_id || index"
        class="rounded-lg border border-slate-100 bg-slate-50/60 px-4 py-3"
      >
        <slot name="item" :item="item">
          <div class="flex items-start justify-between gap-3">
            <div class="min-w-0">
              <p class="text-sm font-medium text-slate-900">
                {{ item.title || item.alert_title || item.event_type || "Activity" }}
              </p>
              <p v-if="item.description" class="mt-1 line-clamp-2 text-xs text-slate-600">
                {{ item.description }}
              </p>
            </div>
            <time v-if="item.created_at || item.timestamp" class="shrink-0 text-xs text-slate-500">
              {{ formatDate(item.created_at || item.timestamp) }}
            </time>
          </div>
        </slot>
      </li>
    </ul>
  </section>
</template>
