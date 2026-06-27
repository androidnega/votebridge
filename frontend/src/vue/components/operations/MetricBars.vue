<script setup>
defineProps({
  title: String,
  items: {
    type: Array,
    default: () => [],
  },
  valueKey: {
    type: String,
    default: "value",
  },
  labelKey: {
    type: String,
    default: "label",
  },
});
</script>

<template>
  <div class="space-y-3">
    <h4 v-if="title" class="text-sm font-semibold text-slate-800">{{ title }}</h4>
    <div v-for="item in items" :key="item[labelKey]" class="space-y-1">
      <div class="flex justify-between text-xs text-slate-600">
        <span>{{ item[labelKey] }}</span>
        <span class="font-medium text-slate-800">{{ item[valueKey] }}</span>
      </div>
      <div class="h-2 overflow-hidden rounded-full bg-surface-muted">
        <div
          class="h-full rounded-full bg-brand-600 transition-all duration-200"
          :style="{ width: `${Math.min(100, item.percent || 0)}%` }"
        />
      </div>
    </div>
  </div>
</template>
