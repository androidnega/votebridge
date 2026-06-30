<script setup>
defineProps({
  current: { type: Number, required: true },
  total: { type: Number, default: 3 },
});

const labels = ["Identity", "Password", "Verify"];
</script>

<template>
  <nav class="mb-5 flex items-center justify-center gap-2" aria-label="Sign-in progress">
    <template v-for="step in total" :key="step">
      <div class="flex flex-col items-center gap-1">
        <span
          class="flex h-7 w-7 items-center justify-center rounded-full text-xs font-semibold transition"
          :class="
            step < current
              ? 'bg-slate-800 text-white'
              : step === current
                ? 'ring-2 ring-slate-800 ring-offset-2 bg-white text-slate-800'
                : 'border border-border bg-white text-slate-400'
          "
        >
          {{ step < current ? "✓" : step }}
        </span>
        <span
          class="text-[10px] font-medium uppercase tracking-wide"
          :class="step === current ? 'text-slate-800' : 'text-slate-400'"
        >
          {{ labels[step - 1] }}
        </span>
      </div>
      <span
        v-if="step < total"
        class="mb-4 h-px w-6 sm:w-10"
        :class="step < current ? 'bg-slate-400' : 'bg-border'"
        aria-hidden="true"
      />
    </template>
  </nav>
</template>
