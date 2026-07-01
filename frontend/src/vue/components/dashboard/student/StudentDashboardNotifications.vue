<script setup>
defineProps({
  items: { type: Array, default: () => [] },
});

function formatWhen(value) {
  if (!value) return "";
  return new Date(value).toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}
</script>

<template>
  <section
    class="rounded-card border border-border bg-surface p-card shadow-card"
    aria-labelledby="student-notifications-heading"
  >
    <h2 id="student-notifications-heading" class="text-sm font-semibold uppercase tracking-wide text-slate-500">
      Recent updates
    </h2>

    <ul v-if="items.length" class="mt-4 space-y-3">
      <li
        v-for="item in items"
        :key="item.uuid || item.id"
        class="rounded-input border border-border bg-surface-muted px-4 py-3"
      >
        <p class="text-sm font-semibold text-slate-900">{{ item.title }}</p>
        <p class="mt-1 text-sm text-slate-600">{{ item.body }}</p>
        <p v-if="item.created_at" class="mt-2 text-xs text-slate-500">{{ formatWhen(item.created_at) }}</p>
      </li>
    </ul>

    <p v-else class="mt-4 text-sm text-slate-600">
      Election announcements will appear here when they are sent.
    </p>
  </section>
</template>
