<script setup>
import VIcon from "@/components/ui/VIcon.vue";

defineProps({
  actions: { type: Array, default: () => [] },
});

defineEmits(["select"]);
</script>

<template>
  <div class="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
    <button
      v-for="action in actions"
      :key="action.id"
      type="button"
      class="flex min-h-[88px] flex-col items-center justify-center gap-2 rounded-2xl border border-border bg-[#F9FAFB] px-3 py-4 text-center transition duration-200 hover:border-[#166534]/30 hover:bg-[#E8F5EE] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#166534]/40"
      @click="$emit('select', action.route)"
    >
      <span
        class="flex h-10 w-10 items-center justify-center rounded-xl bg-white text-[#166534] shadow-[0_1px_2px_0_rgb(15_23_42_/_0.04)]"
        aria-hidden="true"
      >
        <VIcon :name="action.icon || 'elections'" size="sm" />
      </span>
      <span class="text-xs font-medium leading-snug text-ink-primary">{{ action.label }}</span>
    </button>
  </div>
</template>
