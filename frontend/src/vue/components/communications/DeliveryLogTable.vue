<script setup>
import { VButton, VTable } from "@/components/ui";

defineProps({
  items: { type: Array, default: () => [] },
  loading: Boolean,
  showRetry: Boolean,
});

const emit = defineEmits(["retry"]);

const columns = [
  { key: "channel", label: "Channel" },
  { key: "recipient", label: "Recipient" },
  { key: "template_code", label: "Template" },
  { key: "status", label: "Status" },
  { key: "created_at", label: "Created" },
  { key: "actions", label: "" },
];

function formatDate(value) {
  if (!value) return "—";
  return new Date(value).toLocaleString();
}

function statusClass(status) {
  const map = {
    delivered: "text-green-700",
    failed: "text-red-700",
    pending: "text-amber-700",
    retrying: "text-amber-700",
    processing: "text-cyan-700",
  };
  return map[status] || "text-slate-600";
}
</script>

<template>
  <div class="space-y-4">
    <div class="hidden md:block">
      <VTable :columns="columns" :rows="items" :loading="loading" empty-message="No delivery logs found.">
        <template #cell-channel="{ row }">
          <span class="uppercase">{{ row.channel }}</span>
        </template>
        <template #cell-status="{ row }">
          <span class="capitalize" :class="statusClass(row.status)">{{ row.status }}</span>
        </template>
        <template #cell-created_at="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
        <template #cell-actions="{ row }">
          <VButton
            v-if="showRetry && ['failed', 'retrying'].includes(row.status)"
            size="sm"
            variant="secondary"
            @click="emit('retry', row.uuid)"
          >
            Retry
          </VButton>
        </template>
      </VTable>
    </div>

    <div class="space-y-3 md:hidden">
      <div v-if="loading" class="text-sm text-slate-500">Loading delivery logs…</div>
      <div v-else-if="!items.length" class="rounded-xl border border-dashed border-slate-200 p-6 text-center text-sm text-slate-500">
        No delivery logs found.
      </div>
      <article
        v-for="row in items"
        v-else
        :key="row.uuid"
        class="rounded-xl bg-white p-4 shadow-sm ring-1 ring-slate-900/5"
      >
        <div class="flex items-start justify-between gap-2">
          <p class="font-medium capitalize text-slate-900">{{ row.channel }}</p>
          <span class="text-xs capitalize" :class="statusClass(row.status)">{{ row.status }}</span>
        </div>
        <p class="mt-1 truncate text-sm text-slate-600">{{ row.recipient }}</p>
        <p class="mt-1 text-xs text-slate-500">{{ row.template_code }} · {{ formatDate(row.created_at) }}</p>
        <VButton
          v-if="showRetry && ['failed', 'retrying'].includes(row.status)"
          class="mt-3"
          size="sm"
          variant="secondary"
          @click="emit('retry', row.uuid)"
        >
          Retry
        </VButton>
      </article>
    </div>
  </div>
</template>
