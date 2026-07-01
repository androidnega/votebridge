<script setup>
import VIcon from "@/components/ui/VIcon.vue";

defineProps({
  actions: { type: Array, default: () => [] },
});

defineEmits(["select"]);

const severityStyles = {
  certification: "border-l-[#2563EB] bg-[#2563EB]/5",
  ussd: "border-l-[#D97706] bg-[#D97706]/5",
  sms: "border-l-[#D97706] bg-[#D97706]/5",
  backup: "border-l-[#DC2626] bg-[#DC2626]/5",
  maintenance: "border-l-[#0891B2] bg-[#0891B2]/5",
  "maintenance-scheduled": "border-l-[#0891B2] bg-[#0891B2]/5",
  security: "border-l-[#DC2626] bg-[#DC2626]/5",
  default: "border-l-[#64748B] bg-[#F8FAFC]",
};
</script>

<template>
  <ul class="space-y-3">
    <li v-for="action in actions" :key="action.id">
      <button
        type="button"
        class="flex w-full min-h-touch items-center justify-between gap-4 rounded-input border border-[#E5E7EB] border-l-4 px-4 py-3.5 text-left transition hover:shadow-sm"
        :class="severityStyles[action.id] || severityStyles.default"
        @click="$emit('select', action.route)"
      >
        <span class="text-sm font-medium text-[#1F2937]">{{ action.title }}</span>
        <span class="inline-flex shrink-0 items-center gap-1 text-xs font-semibold text-[#2563EB]">
          Review
          <VIcon name="chevronRight" size="sm" />
        </span>
      </button>
    </li>
  </ul>
</template>
