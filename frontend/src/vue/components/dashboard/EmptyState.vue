<script setup>
import { computed } from "vue";
import EmptyState from "@/components/ui/EmptyState.vue";

const props = defineProps({
  title: {
    type: String,
    default: "Nothing here yet",
  },
  description: {
    type: String,
    default: "Check back later for updates.",
  },
  icon: {
    type: String,
    default: "inbox",
  },
});

const isEmoji = computed(() => props.icon.length <= 2);
const iconName = computed(() => (isEmoji.value ? "inbox" : props.icon));
</script>

<template>
  <EmptyState v-if="!isEmoji" :title="title" :description="description" :icon="iconName">
    <template v-if="$slots.action" #action>
      <slot name="action" />
    </template>
  </EmptyState>
  <div
    v-else
    class="flex flex-col items-center justify-center rounded-card border border-dashed border-border bg-surface-muted/50 px-6 py-10 text-center"
  >
    <span class="text-3xl" aria-hidden="true">{{ icon }}</span>
    <h4 class="mt-4 text-sm font-semibold text-slate-800">{{ title }}</h4>
    <p class="mt-1 max-w-sm text-sm text-slate-500">{{ description }}</p>
    <div v-if="$slots.action" class="mt-4">
      <slot name="action" />
    </div>
  </div>
</template>
