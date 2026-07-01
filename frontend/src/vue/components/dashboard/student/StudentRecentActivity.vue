<script setup>
defineProps({
  items: { type: Array, default: () => [] },
});
</script>

<template>
  <section class="student-panel mt-6" aria-labelledby="recent-activity-heading">
    <h2 id="recent-activity-heading" class="mb-4 text-lg font-semibold text-ink-primary">
      Recent activity
    </h2>

    <ul v-if="items.length" class="divide-y divide-border rounded-card border border-border bg-surface shadow-card">
      <li
        v-for="item in items"
        :key="item.id"
        class="flex items-center justify-between gap-4 px-4 py-4"
      >
        <p class="text-sm font-medium text-ink-primary">{{ item.title }}</p>
        <time v-if="item.relative" class="shrink-0 text-xs text-ink-secondary">{{ item.relative }}</time>
      </li>
    </ul>

    <p v-else class="rounded-card border border-border bg-surface px-4 py-6 text-sm text-ink-secondary shadow-card">
      Your voting activity will appear here after you cast a ballot.
    </p>
  </section>
</template>
