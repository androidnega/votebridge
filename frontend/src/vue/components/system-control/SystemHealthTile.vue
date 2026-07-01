<script setup>
import { computed } from "vue";
import OpsHealthBadge from "@/components/operations/OpsHealthBadge.vue";
import { VIcon } from "@/components/ui";
import { normalizeHealthStatus } from "@/config/systemControlHub";

const props = defineProps({
  label: { type: String, required: true },
  status: { type: String, default: "unknown" },
  icon: { type: String, default: "settings" },
  compact: Boolean,
});

const normalized = computed(() => normalizeHealthStatus(props.status));

const ringClass = computed(() => {
  const rings = {
    healthy: "ring-success-200 bg-success-50 text-success-700",
    warning: "ring-warning-200 bg-warning-50 text-warning-700",
    critical: "ring-danger-200 bg-danger-50 text-danger-700",
    unknown: "ring-slate-200 bg-slate-50 text-slate-600",
  };
  return rings[normalized.value] || rings.unknown;
});
</script>

<template>
  <div
    class="flex items-center gap-3 rounded-card border border-border bg-white shadow-card"
    :class="compact ? 'p-3' : 'p-4'"
  >
    <div
      class="flex shrink-0 items-center justify-center rounded-input ring-1"
      :class="[ringClass, compact ? 'h-8 w-8' : 'h-10 w-10']"
      aria-hidden="true"
    >
      <VIcon :name="icon" size="sm" />
    </div>
    <div class="min-w-0 flex-1">
      <p class="truncate text-sm font-medium text-slate-800">{{ label }}</p>
      <OpsHealthBadge :status="normalized" class="mt-1" />
    </div>
  </div>
</template>
