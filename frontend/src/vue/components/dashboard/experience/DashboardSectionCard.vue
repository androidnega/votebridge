<script setup>
defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: "" },
  noPadding: Boolean,
});
</script>

<template>
  <section class="rounded-2xl border border-border bg-white shadow-[0_1px_2px_0_rgb(15_23_42_/_0.04)]">
    <header class="border-b border-border px-6 py-5">
      <div class="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h3 class="text-base font-semibold text-ink-primary">{{ title }}</h3>
          <p v-if="subtitle" class="mt-1 text-sm text-ink-secondary">{{ subtitle }}</p>
        </div>
        <slot name="actions" />
      </div>
    </header>
    <div :class="noPadding ? '' : 'p-6'">
      <slot />
    </div>
  </section>
</template>
