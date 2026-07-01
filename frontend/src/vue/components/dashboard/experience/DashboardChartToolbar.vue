<script setup>
defineProps({
  ranges: { type: Array, default: () => [] },
  modelValue: { type: String, default: "today" },
});

defineEmits(["update:modelValue"]);
</script>

<template>
  <div class="inline-flex flex-wrap gap-1 rounded-xl bg-[#F3F4F6] p-1">
    <button
      v-for="range in ranges"
      :key="range.id"
      type="button"
      class="rounded-lg px-3 py-1.5 text-xs font-medium transition duration-200"
      :class="
        modelValue === range.id
          ? 'bg-white text-ink-primary shadow-sm'
          : 'text-ink-secondary hover:text-ink-primary'
      "
      @click="$emit('update:modelValue', range.id)"
    >
      {{ range.label }}
    </button>
  </div>
</template>
