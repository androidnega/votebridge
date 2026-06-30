<script setup>
defineProps({
  stages: { type: Array, default: () => [] },
  currentStage: { type: String, default: "draft" },
});

const stageOrder = ["draft", "scheduled", "open", "closed", "certified", "published"];

function stageIndex(id) {
  return stageOrder.indexOf(id);
}
</script>

<template>
  <ol class="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
    <li
      v-for="stage in stages"
      :key="stage.id"
      class="rounded-input border px-3 py-4 text-center transition"
      :class="
        stage.id === currentStage
          ? 'border-[#2563EB] bg-[#EFF6FF] text-[#2563EB]'
          : stageIndex(stage.id) < stageIndex(currentStage)
            ? 'border-[#BBF7D0] bg-[#F0FDF4] text-[#16A34A]'
            : 'border-[#E5E7EB] bg-[#F8FAFC] text-[#64748B]'
      "
    >
      <p class="text-xs font-semibold uppercase tracking-wide">{{ stage.label }}</p>
      <p v-if="stage.id === currentStage" class="mt-2 text-[0.6875rem] font-medium">Current</p>
    </li>
  </ol>
</template>
