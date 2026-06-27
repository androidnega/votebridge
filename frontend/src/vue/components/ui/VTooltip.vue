<script setup>
defineProps({
  label: {
    type: String,
    required: true,
  },
  position: {
    type: String,
    default: "right",
    validator: (v) => ["right", "top", "bottom"].includes(v),
  },
});
</script>

<template>
  <div class="group relative inline-flex">
    <slot />
    <span
      role="tooltip"
      class="pointer-events-none absolute z-50 whitespace-nowrap rounded-input bg-slate-900 px-2.5 py-1.5 text-xs font-medium text-white opacity-0 shadow-card transition-opacity duration-200 group-hover:opacity-100 group-focus-within:opacity-100"
      :class="{
        'left-full top-1/2 ml-2 -translate-y-1/2': position === 'right',
        'bottom-full left-1/2 mb-2 -translate-x-1/2': position === 'top',
        'left-1/2 top-full mt-2 -translate-x-1/2': position === 'bottom',
      }"
    >
      {{ label }}
    </span>
  </div>
</template>
