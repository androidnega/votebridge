<script setup>
import { computed } from "vue";
import VIcon from "@/components/ui/VIcon.vue";

const props = defineProps({
  id: { type: String, default: "" },
  title: { type: String, required: true },
  value: { type: [String, Number], default: "—" },
  detail: { type: String, default: "" },
  hint: { type: String, default: "" },
  healthStatus: { type: String, default: "" },
  clickable: Boolean,
});

defineEmits(["click"]);

const icons = {
  "platform-health": "operations",
  "platform-state": "elections",
  "pending-certification": "results",
  "security-alerts": "security",
  infrastructure: "bolt",
};

const accent = computed(() => {
  const map = {
    healthy: "bg-[#CBD5E1]",
    warning: "bg-[#D6D3D1]",
    critical: "bg-[#D4A4A4]",
    unknown: "bg-[#E2E8F0]",
  };
  return map[props.healthStatus] || map.unknown;
});
</script>

<template>
  <article
    class="group relative flex min-h-[148px] flex-col overflow-hidden rounded-card border border-[#E5E7EB] bg-white shadow-[0_1px_3px_0_rgb(15_23_42_/_0.06)] transition-all"
    :class="clickable ? 'cursor-pointer hover:border-[#CBD5E1] hover:shadow-md' : ''"
    @click="clickable ? $emit('click') : undefined"
  >
    <span
      v-if="healthStatus"
      class="absolute inset-x-0 top-0 h-1"
      :class="accent"
      aria-hidden="true"
    />

    <div class="flex flex-1 flex-col p-5 pt-6">
      <div class="flex items-start justify-between gap-3">
        <p class="text-sm font-medium text-[#64748B]">{{ title }}</p>
        <span
          class="flex h-9 w-9 shrink-0 items-center justify-center rounded-input bg-[#F8FAFC] text-[#64748B] ring-1 ring-[#E5E7EB]"
          aria-hidden="true"
        >
          <VIcon :name="icons[id] || 'settings'" size="sm" />
        </span>
      </div>

      <div class="mt-4 flex-1">
        <p class="text-2xl font-semibold tracking-tight capitalize text-[#1F2937]">
          {{ value }}
        </p>
        <p v-if="detail" class="mt-1 text-sm font-medium text-[#1F2937]">{{ detail }}</p>
      </div>

      <p v-if="hint" class="mt-4 border-t border-[#E5E7EB] pt-3 text-xs leading-relaxed text-[#64748B]">
        {{ hint }}
      </p>
    </div>
  </article>
</template>
