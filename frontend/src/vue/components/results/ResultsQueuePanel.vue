<script setup>
import { VButton } from "@/components/ui";
import ResultStatusBadge from "./ResultStatusBadge.vue";

defineProps({
  items: { type: Array, default: () => [] },
  loading: Boolean,
  emptyTitle: { type: String, default: "Queue empty" },
  emptyDescription: { type: String, default: "No elections in this queue." },
  actionLabel: String,
  actionLoading: Boolean,
});

const emit = defineEmits(["action", "select"]);
</script>

<template>
  <section class="rounded-xl bg-white shadow-sm ring-1 ring-slate-900/5">
    <div v-if="loading" class="p-8 text-center text-sm text-slate-500">Loading…</div>
    <div v-else-if="!items.length" class="p-8 text-center">
      <p class="font-medium text-slate-900">{{ emptyTitle }}</p>
      <p class="mt-1 text-sm text-slate-500">{{ emptyDescription }}</p>
    </div>
    <ul v-else class="divide-y divide-slate-100">
      <li
        v-for="item in items"
        :key="item.uuid || item.election_uuid"
        class="flex flex-col gap-3 p-4 sm:flex-row sm:items-center sm:justify-between"
      >
        <button
          type="button"
          class="text-left focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-600"
          @click="emit('select', item)"
        >
          <p class="font-medium text-slate-900">{{ item.election_title }}</p>
          <div class="mt-1 flex flex-wrap items-center gap-2">
            <ResultStatusBadge :status="item.result_status" />
            <span v-if="item.turnout_percentage !== undefined" class="text-xs text-slate-500">
              Turnout {{ item.turnout_percentage }}%
            </span>
          </div>
        </button>
        <VButton
          v-if="actionLabel"
          size="sm"
          :loading="actionLoading"
          @click="emit('action', item)"
        >
          {{ actionLabel }}
        </VButton>
      </li>
    </ul>
  </section>
</template>
