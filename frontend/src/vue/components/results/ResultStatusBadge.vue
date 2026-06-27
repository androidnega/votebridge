<script setup>
import { computed } from "vue";

const props = defineProps({
  status: { type: String, required: true },
});

const classes = computed(() => ({
  pending_generation: "bg-slate-100 text-slate-700 ring-slate-200",
  generated: "bg-blue-50 text-blue-700 ring-blue-200",
  pending_certification: "bg-amber-50 text-amber-700 ring-amber-200",
  certified: "bg-indigo-50 text-indigo-700 ring-indigo-200",
  published: "bg-green-50 text-green-700 ring-green-200",
  archived: "bg-slate-200 text-slate-600 ring-slate-300",
}[props.status] || "bg-slate-100 text-slate-700 ring-slate-200"));

const label = computed(() => props.status?.replace(/_/g, " ") || "unknown");
</script>

<template>
  <span
    class="inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium capitalize ring-1 ring-inset"
    :class="classes"
  >
    {{ label }}
  </span>
</template>
