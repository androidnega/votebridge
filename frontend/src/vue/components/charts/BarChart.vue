<script setup>
import { computed } from "vue";
import { CHART_COLORS, useEChart } from "./useEChart";

const props = defineProps({
  title: String,
  labels: { type: Array, default: () => [] },
  values: { type: Array, default: () => [] },
  horizontal: Boolean,
  height: { type: String, default: "280px" },
});

const option = computed(() => ({
  color: CHART_COLORS,
  title: props.title ? { text: props.title, left: 0, textStyle: { fontSize: 14, fontWeight: 600 } } : undefined,
  tooltip: { trigger: "axis" },
  grid: { left: 40, right: 16, top: props.title ? 48 : 24, bottom: 32 },
  xAxis: props.horizontal ? { type: "value" } : { type: "category", data: props.labels },
  yAxis: props.horizontal ? { type: "category", data: props.labels } : { type: "value" },
  series: [{ type: "bar", data: props.values, itemStyle: { borderRadius: [4, 4, 0, 0] } }],
}));

const { elRef } = useEChart(option);
</script>

<template>
  <div ref="elRef" class="w-full" :style="{ height }" role="img" :aria-label="title || 'Bar chart'" />
</template>
