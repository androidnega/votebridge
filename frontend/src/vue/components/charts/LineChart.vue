<script setup>
import { computed } from "vue";
import { CHART_COLORS, useEChart } from "./useEChart";

const props = defineProps({
  title: String,
  labels: { type: Array, default: () => [] },
  series: { type: Array, default: () => [] },
  height: { type: String, default: "280px" },
});

const option = computed(() => ({
  color: CHART_COLORS,
  title: props.title ? { text: props.title, left: 0, textStyle: { fontSize: 14, fontWeight: 600 } } : undefined,
  tooltip: { trigger: "axis" },
  grid: { left: 40, right: 16, top: props.title ? 48 : 24, bottom: 32 },
  xAxis: { type: "category", data: props.labels, boundaryGap: false },
  yAxis: { type: "value", splitLine: { lineStyle: { color: "#E2E8F0" } } },
  series: props.series.map((s) => ({
    type: "line",
    smooth: true,
    showSymbol: false,
    areaStyle: s.area ? { opacity: 0.08 } : undefined,
    ...s,
  })),
}));

const { elRef } = useEChart(option);
</script>

<template>
  <div ref="elRef" class="w-full" :style="{ height }" role="img" :aria-label="title || 'Line chart'" />
</template>
