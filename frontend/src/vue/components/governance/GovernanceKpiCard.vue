<script setup>
import OpsHealthBadge from "@/components/operations/OpsHealthBadge.vue";

defineProps({
  title: { type: String, required: true },
  value: { type: [String, Number], default: "—" },
  detail: { type: String, default: "" },
  hint: { type: String, default: "" },
  healthStatus: { type: String, default: "" },
  clickable: Boolean,
});

defineEmits(["click"]);
</script>

<template>
  <article
    class="flex flex-col rounded-card border border-[#E5E7EB] bg-white p-5 shadow-[0_1px_3px_0_rgb(15_23_42_/_0.06)] transition-colors"
    :class="clickable ? 'cursor-pointer hover:border-[#2563EB]/30 hover:shadow-md' : ''"
    @click="clickable ? $emit('click') : undefined"
  >
    <p class="text-sm font-medium text-[#64748B]">{{ title }}</p>
    <div class="mt-3 flex items-center gap-2">
      <p class="text-2xl font-semibold tracking-tight text-[#1F2937]">{{ value }}</p>
      <OpsHealthBadge v-if="healthStatus" :status="healthStatus" />
    </div>
    <p v-if="detail" class="mt-1 text-sm font-medium text-[#1F2937]">{{ detail }}</p>
    <p v-if="hint" class="mt-2 text-xs leading-relaxed text-[#64748B]">{{ hint }}</p>
  </article>
</template>
