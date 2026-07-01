<script setup>
defineProps({
  label: { type: String, default: "Closes in" },
  days: { type: Number, default: 0 },
  hours: { type: Number, default: 0 },
  minutes: { type: Number, default: 0 },
  expired: { type: Boolean, default: false },
});
</script>

<template>
  <section
    class="rounded-card border border-border bg-surface p-card shadow-card"
    aria-labelledby="student-countdown-heading"
  >
    <h2 id="student-countdown-heading" class="text-sm font-semibold uppercase tracking-wide text-slate-500">
      {{ label }}
    </h2>
    <p v-if="expired" class="mt-4 text-2xl font-bold text-slate-900">Voting window ended</p>
    <div v-else class="mt-4 grid grid-cols-3 gap-3">
      <div class="rounded-input bg-brand-50 px-3 py-4 text-center">
        <p class="text-3xl font-bold tabular-nums text-brand-700">{{ days }}</p>
        <p class="mt-1 text-xs font-medium uppercase tracking-wide text-slate-600">Days</p>
      </div>
      <div class="rounded-input bg-brand-50 px-3 py-4 text-center">
        <p class="text-3xl font-bold tabular-nums text-brand-700">{{ hours }}</p>
        <p class="mt-1 text-xs font-medium uppercase tracking-wide text-slate-600">Hours</p>
      </div>
      <div class="rounded-input bg-brand-50 px-3 py-4 text-center">
        <p class="text-3xl font-bold tabular-nums text-brand-700">{{ minutes }}</p>
        <p class="mt-1 text-xs font-medium uppercase tracking-wide text-slate-600">Minutes</p>
      </div>
    </div>
  </section>
</template>
