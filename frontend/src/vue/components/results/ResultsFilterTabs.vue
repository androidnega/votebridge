<script setup>
defineProps({
  tabs: {
    type: Array,
    required: true,
    // { id, label, count, description? }
  },
  active: {
    type: String,
    default: "all",
  },
});

const emit = defineEmits(["change"]);
</script>

<template>
  <div
    class="flex flex-col gap-3 rounded-card border border-border bg-surface p-2 shadow-sm sm:flex-row sm:items-stretch sm:p-2"
    role="tablist"
    aria-label="Filter results by status"
  >
    <button
      v-for="tab in tabs"
      :key="tab.id"
      type="button"
      role="tab"
      class="flex min-w-0 flex-1 flex-col rounded-lg px-4 py-3 text-left transition"
      :class="
        active === tab.id
          ? 'bg-brand-600 text-white shadow-sm'
          : 'text-slate-700 hover:bg-slate-50'
      "
      :aria-selected="active === tab.id"
      @click="emit('change', tab.id)"
    >
      <span class="flex items-center justify-between gap-2">
        <span class="text-sm font-semibold">{{ tab.label }}</span>
        <span
          class="inline-flex min-w-[1.5rem] items-center justify-center rounded-full px-2 py-0.5 text-xs font-bold tabular-nums"
          :class="active === tab.id ? 'bg-white/20 text-white' : 'bg-slate-100 text-slate-700'"
        >
          {{ tab.count }}
        </span>
      </span>
      <span
        class="mt-1 text-xs leading-relaxed"
        :class="active === tab.id ? 'text-brand-100' : 'text-slate-500'"
      >
        {{ tab.description }}
      </span>
    </button>
  </div>
</template>
