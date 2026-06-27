<script setup>
import OpsHealthBadge from "./OpsHealthBadge.vue";
import { VCard } from "@/components/ui";

defineProps({
  nodes: { type: Array, default: () => [] },
  links: { type: Array, default: () => [] },
});

const layerOrder = ["client", "application", "realtime", "cache", "data", "integration", "integrity"];
</script>

<template>
  <div class="grid grid-cols-1 gap-4 lg:grid-cols-2 xl:grid-cols-3">
    <div
      v-for="layer in layerOrder"
      :key="layer"
      class="rounded-card border border-border bg-white p-card shadow-card"
    >
      <h4 class="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-500">{{ layer }}</h4>
      <ul class="space-y-2">
        <li
          v-for="node in nodes.filter((n) => n.layer === layer)"
          :key="node.id"
          class="flex items-center justify-between rounded-input bg-surface-muted px-3 py-2"
        >
          <span class="text-sm font-medium text-slate-800">{{ node.label }}</span>
          <OpsHealthBadge :status="node.status" />
        </li>
      </ul>
    </div>
  </div>

  <VCard v-if="links.length" title="Service relationships" class="mt-4">
    <ul class="grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-3">
      <li
        v-for="(link, index) in links"
        :key="index"
        class="rounded-input bg-surface-muted px-3 py-2 text-sm text-slate-700"
      >
        {{ link.from }} → {{ link.to }}
      </li>
    </ul>
  </VCard>
</template>
