<script setup>
import { computed } from "vue";
import ActivityFeed from "./ActivityFeed.vue";
import ConnectionStatusIndicator from "./ConnectionStatusIndicator.vue";

const props = defineProps({
  items: {
    type: Array,
    default: () => [],
  },
  loading: Boolean,
  status: {
    type: String,
    default: "disconnected",
  },
  title: {
    type: String,
    default: "Live security feed",
  },
  emptyTitle: {
    type: String,
    default: "No security alerts",
  },
  emptyDescription: {
    type: String,
    default: "Security alerts will appear here in real time.",
  },
});

const showLiveBadge = computed(() => props.status === "connected" || props.status === "connecting");
</script>

<template>
  <div class="space-y-3">
    <div v-if="showLiveBadge" class="flex justify-end">
      <ConnectionStatusIndicator :status="status" />
    </div>
    <ActivityFeed
      :title="title"
      :items="items"
      :loading="loading"
      :empty-title="emptyTitle"
      :empty-description="emptyDescription"
    >
      <template #item="{ item }">
        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0">
            <p class="text-sm font-medium text-slate-900">
              {{ item.title || item.alert_title || "Security alert" }}
            </p>
            <p v-if="item.description" class="mt-1 line-clamp-2 text-xs text-slate-600">
              {{ item.description }}
            </p>
            <p v-if="item.alert_type" class="mt-1 text-xs font-medium uppercase text-red-600">
              {{ item.alert_type }}
            </p>
          </div>
          <time v-if="item.created_at" class="shrink-0 text-xs text-slate-500">
            {{ new Date(item.created_at).toLocaleString(undefined, { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }) }}
          </time>
        </div>
      </template>
    </ActivityFeed>
  </div>
</template>
