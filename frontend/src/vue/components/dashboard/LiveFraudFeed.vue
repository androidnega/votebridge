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
    default: "Live fraud feed",
  },
  emptyTitle: {
    type: String,
    default: "No fraud cases",
  },
  emptyDescription: {
    type: String,
    default: "Fraud investigations will appear here in real time.",
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
              {{ item.alert_title || item.title || "Fraud case" }}
            </p>
            <p class="mt-1 text-xs text-slate-600">
              <span class="font-medium capitalize">{{ item.severity || "unknown" }}</span>
              <span v-if="item.risk_score !== undefined"> · Risk {{ item.risk_score }}</span>
              <span v-if="item.status"> · {{ item.status }}</span>
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
