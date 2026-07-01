<script setup>
import { computed } from "vue";
import { CHART_COLORS, useEChart } from "./useEChart";

const props = defineProps({
  title: String,
  items: { type: Array, default: () => [] },
  donut: Boolean,
  animated: { type: Boolean, default: true },
  colors: { type: Array, default: null },
  height: { type: String, default: "280px" },
});

const option = computed(() => ({
  color: props.colors?.length ? props.colors : CHART_COLORS,
  animation: props.animated,
  animationDuration: 200,
  animationDurationUpdate: 200,
  title: props.title ? { text: props.title, left: 0, textStyle: { fontSize: 14, fontWeight: 600 } } : undefined,
  tooltip: { trigger: "item" },
  legend: { bottom: 0, type: "scroll" },
  series: [
    {
      type: "pie",
      radius: props.donut ? ["45%", "70%"] : "65%",
      center: ["50%", "45%"],
      data: props.items,
      label: { formatter: "{b}: {d}%" },
    },
  ],
}));

const { elRef } = useEChart(option);
</script>

<template>
  <div ref="elRef" class="w-full" :style="{ height }" role="img" :aria-label="title || 'Pie chart'" />
</template>
