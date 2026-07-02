<script setup>
defineProps({
  label: { type: String, default: "Closes in" },
  parts: {
    type: Object,
    default: () => ({ days: 0, hours: 0, minutes: 0, seconds: 0 }),
  },
});

const units = [
  { key: "days", label: "Days" },
  { key: "hours", label: "Hours" },
  { key: "minutes", label: "Mins" },
  { key: "seconds", label: "Secs" },
];
</script>

<template>
  <div class="rounded-card border border-white/20 bg-white/10 p-3 backdrop-blur-sm sm:p-3.5">
    <p class="text-center text-[10px] font-semibold uppercase tracking-[0.18em] text-white/80">
      {{ label }}
    </p>
    <div class="mt-2.5 grid grid-cols-2 gap-2 sm:grid-cols-4">
      <div
        v-for="unit in units"
        :key="unit.key"
        class="rounded-input bg-white/95 px-1.5 py-2 text-center shadow-sm sm:px-2"
      >
        <p class="text-lg font-bold tabular-nums leading-none text-brand-800 sm:text-xl">
          {{ String(parts[unit.key] ?? 0).padStart(2, "0") }}
        </p>
        <p class="mt-1 text-[9px] font-medium uppercase tracking-wide text-slate-500 sm:text-[10px]">
          {{ unit.label }}
        </p>
      </div>
    </div>
  </div>
</template>
