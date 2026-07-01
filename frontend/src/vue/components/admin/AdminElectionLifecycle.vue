<script setup>
import { computed } from "vue";

const props = defineProps({
  stages: { type: Array, default: () => [] },
  currentStage: { type: String, default: "draft" },
});

const stageOrder = ["draft", "scheduled", "open", "closed", "certified", "published"];

function stageIndex(id) {
  return stageOrder.indexOf(id);
}

function stageState(id) {
  const current = stageIndex(props.currentStage);
  const index = stageIndex(id);
  if (id === props.currentStage) return "current";
  if (index >= 0 && current >= 0 && index < current) return "complete";
  return "upcoming";
}

const stageStyles = {
  current: {
    card: "border-[#2563EB] bg-[#EFF6FF] text-[#2563EB] ring-2 ring-[#2563EB]/15",
    badge: "bg-[#2563EB] text-white",
  },
  complete: {
    card: "border-[#BBF7D0] bg-[#F0FDF4] text-[#16A34A]",
    badge: "text-[#16A34A]",
  },
  upcoming: {
    card: "border-[#E5E7EB] bg-[#F8FAFC] text-[#64748B]",
    badge: "text-[#64748B]",
  },
};

const enrichedStages = computed(() =>
  props.stages.map((stage) => ({
    ...stage,
    state: stageState(stage.id),
    styles: stageStyles[stageState(stage.id)],
  }))
);
</script>

<template>
  <ol
    class="grid min-w-0 gap-2 sm:gap-3 [grid-template-columns:repeat(auto-fit,minmax(5.5rem,1fr))]"
    aria-label="Election lifecycle stages"
  >
    <li
      v-for="stage in enrichedStages"
      :key="stage.id"
      class="min-w-0"
      :aria-current="stage.state === 'current' ? 'step' : undefined"
    >
      <div
        class="flex h-full min-h-[4.5rem] flex-col items-center justify-center rounded-input border px-2 py-2.5 text-center sm:min-h-[5rem] sm:px-3 sm:py-3"
        :class="stage.styles.card"
      >
        <p class="w-full text-xs font-semibold leading-snug text-balance break-words sm:text-sm">
          {{ stage.label }}
        </p>
        <span
          v-if="stage.state === 'current'"
          class="mt-1.5 inline-flex max-w-full items-center justify-center rounded-full px-2 py-0.5 text-[0.625rem] font-semibold leading-none"
          :class="stage.styles.badge"
        >
          Current
        </span>
        <span
          v-else-if="stage.state === 'complete'"
          class="mt-1.5 text-[0.625rem] font-medium leading-none text-[#16A34A]"
        >
          Done
        </span>
      </div>
    </li>
  </ol>
</template>
