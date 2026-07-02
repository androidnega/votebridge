<script setup>
import { computed } from "vue";
import VIcon from "@/components/ui/VIcon.vue";
import { getCommandKpiPalette } from "@/config/adminCommandCenter";

const props = defineProps({
  id: { type: String, default: "" },
  title: { type: String, required: true },
  value: { type: [String, Number], default: "—" },
  detail: { type: String, default: "" },
  hint: { type: String, default: "" },
  healthStatus: { type: String, default: "" },
  clickable: Boolean,
  active: Boolean,
});

defineEmits(["click"]);

const icons = {
  "active-elections": "elections",
  turnout: "analytics",
  "votes-eligible": "profile",
  "pending-tasks": "tasks",
  "election-status": "elections",
};

const palette = computed(() => getCommandKpiPalette(props.id, props.healthStatus));

const iconStyle = computed(() => ({
  backgroundColor: palette.value.iconBg,
  color: palette.value.icon,
  boxShadow: `inset 0 0 0 1px ${palette.value.border}`,
}));

const footerStyle = computed(() => ({
  backgroundColor: palette.value.iconBg,
  color: palette.value.icon,
}));
</script>

<template>
  <article
    class="flex min-h-[148px] flex-col rounded-card border bg-white p-4 shadow-[0_1px_3px_0_rgb(15_23_42_/_0.06)] transition-all sm:p-5"
    :class="[
      active
        ? 'border-brand-400 ring-2 ring-brand-200'
        : 'border-[#E5E7EB]',
      clickable
        ? 'cursor-pointer hover:-translate-y-0.5 hover:border-[#CBD5E1] hover:shadow-[0_8px_20px_-6px_rgb(15_23_42_/_0.12)]'
        : '',
    ]"
    :role="clickable ? 'button' : undefined"
    :tabindex="clickable ? 0 : undefined"
    :aria-pressed="clickable ? active : undefined"
    @click="clickable ? $emit('click') : undefined"
    @keydown.enter.prevent="clickable ? $emit('click') : undefined"
    @keydown.space.prevent="clickable ? $emit('click') : undefined"
  >
    <div class="flex items-center gap-3">
      <span
        class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl"
        :style="iconStyle"
        aria-hidden="true"
      >
        <VIcon :name="icons[id] || 'elections'" size="sm" />
      </span>
      <p class="min-w-0 text-sm font-medium leading-snug text-[#64748B]">{{ title }}</p>
    </div>

    <div class="mt-4 flex-1">
      <p
        class="text-[1.875rem] font-semibold leading-none tracking-tight tabular-nums sm:text-[2rem]"
        :style="{ color: palette.valueColor }"
      >
        {{ value }}
      </p>
      <p v-if="detail" class="mt-2 text-sm font-medium text-[#475569]">{{ detail }}</p>
    </div>

    <p
      v-if="hint"
      class="mt-4 rounded-lg px-3 py-2 text-xs leading-relaxed"
      :style="footerStyle"
    >
      {{ hint }}
      <span v-if="clickable && !active" class="mt-1 block font-medium opacity-80">Click to filter</span>
      <span v-else-if="clickable && active" class="mt-1 block font-semibold">Filter active</span>
    </p>
  </article>
</template>
