<script setup>
import { EmptyState, LoadingSkeleton } from "@/components/dashboard";

defineProps({
  items: { type: Array, default: () => [] },
  loading: Boolean,
});
</script>

<template>
  <section class="rounded-xl bg-white p-5 shadow-sm ring-1 ring-slate-900/5 sm:p-6">
    <h3 class="text-lg font-semibold text-slate-900">Chain of custody</h3>
    <p class="mt-1 text-sm text-slate-500">Immutable audit trail of integrity actions.</p>

    <LoadingSkeleton v-if="loading" class="mt-4" variant="list" :rows="3" />

    <EmptyState
      v-else-if="!items.length"
      class="mt-4 border-0 bg-transparent"
      title="No custody records yet"
      description="Integrity actions such as ballot sealing and election certification appear here."
      icon="📋"
    />

    <ol v-else class="relative mt-6 space-y-6 border-l border-slate-200 pl-6">
      <li v-for="item in items" :key="item.uuid" class="relative">
        <span
          class="absolute -left-[1.6rem] top-1 flex h-3 w-3 rounded-full bg-brand-600 ring-4 ring-white"
          aria-hidden="true"
        />
        <div class="rounded-lg bg-slate-50 px-4 py-3">
          <div class="flex flex-wrap items-start justify-between gap-2">
            <p class="font-medium capitalize text-slate-900">{{ item.action.replace(/_/g, " ") }}</p>
            <time class="text-xs text-slate-500">{{ new Date(item.timestamp).toLocaleString() }}</time>
          </div>
          <p class="mt-1 text-sm text-slate-600">{{ item.actor_name || "System" }}</p>
        </div>
      </li>
    </ol>
  </section>
</template>
