<script setup>
defineProps({
  label: { type: String, default: "Closes in" },
  parts: {
    type: Object,
    default: () => ({ days: 0, hours: 0, minutes: 0, seconds: 0 }),
  },
  compact: Boolean,
});
</script>

<template>
  <div
    class="rounded-card border border-white/20 bg-white/10 p-4 backdrop-blur-sm"
    :class="compact ? 'p-3' : 'p-4'"
  >
    <p class="text-center text-[10px] font-semibold uppercase tracking-[0.2em] text-white/80">
      {{ label }}
    </p>
    <div class="mt-3 grid grid-cols-3 gap-2">
      <div
        v-for="unit in [
          { key: 'days', label: 'Days' },
          { key: 'hours', label: 'Hours' },
          { key: 'minutes', label: 'Mins' },
        ]"
        :key="unit.key"
        class="rounded-input bg-white/95 px-2 py-2 text-center shadow-sm"
      >
        <p class="text-xl font-bold tabular-nums leading-none text-brand-800 sm:text-2xl">
          {{ String(parts[unit.key] ?? 0).padStart(2, "0") }}
        </p>
        <p class="mt-1 text-[10px] font-medium uppercase tracking-wide text-slate-500">
          {{ unit.label }}
        </p>
      </div>
    </div>
  </div>
</template>
