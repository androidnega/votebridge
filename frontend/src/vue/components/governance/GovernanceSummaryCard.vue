<script setup>
import { VButton } from "@/components/ui";

defineProps({
  title: { type: String, required: true },
  count: { type: [String, Number], default: "—" },
  description: { type: String, default: "" },
  actionLabel: { type: String, default: "View" },
  loading: Boolean,
});

defineEmits(["view"]);
</script>

<template>
  <article class="vb-kpi-card flex flex-col">
    <p class="text-sm font-medium text-ink-secondary">{{ title }}</p>
    <div v-if="loading" class="mt-2 h-9 w-16 animate-pulse rounded-lg bg-surface-muted" />
    <p v-else class="mt-2 text-3xl font-semibold tabular-nums tracking-tight text-ink-primary">
      {{ count }}
    </p>
    <p v-if="description" class="mt-2 flex-1 text-xs leading-relaxed text-ink-secondary">
      {{ description }}
    </p>
    <div class="mt-4 border-t border-border pt-3">
      <VButton size="sm" variant="secondary" class="w-full sm:w-auto" @click="$emit('view')">
        {{ actionLabel }}
      </VButton>
    </div>
  </article>
</template>
