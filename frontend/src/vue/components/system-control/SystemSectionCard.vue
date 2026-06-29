<script setup>
import { VIcon } from "@/components/ui";

defineProps({
  title: { type: String, required: true },
  description: { type: String, default: "" },
  icon: { type: String, default: "settings" },
  items: { type: Array, default: () => [] },
});
</script>

<template>
  <article class="flex h-full flex-col rounded-card border border-border bg-white shadow-card">
    <header class="border-b border-border px-card pb-4 pt-card">
      <div class="flex items-start gap-3">
        <div
          class="flex h-10 w-10 shrink-0 items-center justify-center rounded-input bg-brand-50 text-brand-700"
          aria-hidden="true"
        >
          <VIcon :name="icon" size="sm" />
        </div>
        <div class="min-w-0">
          <h3 class="text-base font-semibold text-slate-900">{{ title }}</h3>
          <p v-if="description" class="mt-1 text-sm text-slate-500">{{ description }}</p>
        </div>
      </div>
    </header>

    <ul class="flex flex-1 flex-col divide-y divide-border">
      <li v-for="item in items" :key="item.to">
        <router-link
          :to="item.to"
          class="group flex min-h-touch items-start justify-between gap-3 px-card py-4 transition-colors hover:bg-surface-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-brand-600"
        >
          <span class="min-w-0">
            <span class="block text-sm font-medium text-slate-800 group-hover:text-brand-700">
              {{ item.label }}
            </span>
            <span v-if="item.description" class="mt-0.5 block text-xs text-slate-500">
              {{ item.description }}
            </span>
          </span>
          <VIcon
            name="chevronRight"
            size="sm"
            class="mt-0.5 shrink-0 text-slate-400 transition-transform group-hover:translate-x-0.5 group-hover:text-brand-600"
          />
        </router-link>
      </li>
    </ul>
  </article>
</template>
