<script setup>
import { computed } from "vue";
import { StatusBadge, VCard } from "@/components/ui";

const props = defineProps({
  status: { type: Object, default: null },
  loading: { type: Boolean, default: false },
});

const badgeVariant = computed(() => {
  if (!props.status?.enrolled) return "grey";
  if (props.status?.is_locked) return "danger";
  return "success";
});

const badgeLabel = computed(() => {
  if (!props.status?.enrolled) return "Not enrolled";
  if (props.status?.is_locked) return "Locked";
  return "Enrolled";
});
</script>

<template>
  <VCard title="Biometric status">
    <div v-if="loading" class="text-sm text-slate-500">Loading status…</div>
    <div v-else-if="status" class="space-y-3">
      <div class="flex items-center gap-3">
        <StatusBadge :variant="badgeVariant" :label="badgeLabel" />
        <span v-if="status.last_verified_at" class="text-sm text-slate-600">
          Last verified {{ new Date(status.last_verified_at).toLocaleString() }}
        </span>
      </div>
      <dl class="grid grid-cols-2 gap-3 text-sm">
        <div>
          <dt class="text-slate-500">Quality score</dt>
          <dd class="font-medium">{{ status.quality_score?.toFixed(2) ?? "—" }}</dd>
        </div>
        <div>
          <dt class="text-slate-500">Model</dt>
          <dd class="font-medium">{{ status.model_version || "—" }}</dd>
        </div>
      </dl>
    </div>
  </VCard>
</template>
