<script setup>
import { computed } from "vue";
import { CHART_COLORS, useEChart } from "./useEChart";

const props = defineProps({
  title: String,
  labels: { type: Array, default: () => [] },
  points: { type: Array, default: () => [] },
  height: { type: String, default: "280px" },
  yAxisName: { type: String, default: "" },
});

const option = computed(() => ({
  color: CHART_COLORS,
  title: props.title ? { text: props.title, left: 0, textStyle: { fontSize: 14, fontWeight: 600 } } : undefined,
  tooltip: {
    trigger: "item",
    formatter: (params) => {
      const [, count, size] = params.value;
      return `${params.name}<br/>${count} events · intensity ${size}`;
    },
  },
  grid: { left: 48, right: 16, top: props.title ? 48 : 24, bottom: 32 },
  xAxis: {
    type: "category",
    data: props.labels,
    boundaryGap: true,
    axisLabel: { color: "#64748B", fontSize: 11 },
  },
  yAxis: {
    type: "value",
    name: props.yAxisName,
    splitLine: { lineStyle: { color: "#E2E8F0" } },
    axisLabel: { color: "#64748B" },
  },
  series: [
    {
      type: "scatter",
      data: props.points.map((point, index) => ({
        name: point.name || props.labels[index] || `Hour ${index + 1}`,
        value: [index, point.y, point.size],
      })),
      symbolSize: (data) => data[2],
      itemStyle: { opacity: 0.82 },
      emphasis: { scale: 1.08 },
    },
  ],
}));

const { elRef } = useEChart(option);
</script>

<template>
  <div ref="elRef" class="w-full" :style="{ height }" role="img" :aria-label="title || 'Bubble chart'" />
</template>
