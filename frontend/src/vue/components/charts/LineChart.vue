<script setup>
import { computed } from "vue";
import { CHART_COLORS, useEChart } from "./useEChart";

const props = defineProps({
  title: String,
  labels: { type: Array, default: () => [] },
  series: { type: Array, default: () => [] },
  smooth: { type: Boolean, default: true },
  animated: { type: Boolean, default: true },
  height: { type: String, default: "280px" },
});

const option = computed(() => ({
  color: CHART_COLORS,
  animation: props.animated,
  animationDuration: 200,
  animationDurationUpdate: 200,
  title: props.title ? { text: props.title, left: 0, textStyle: { fontSize: 14, fontWeight: 600 } } : undefined,
  tooltip: { trigger: "axis" },
  grid: { left: 40, right: 16, top: props.title ? 48 : 24, bottom: 32 },
  xAxis: { type: "category", data: props.labels, boundaryGap: false },
  yAxis: { type: "value", splitLine: { lineStyle: { color: "#E5E7EB" } } },
  series: props.series.map((s) => {
    const color = s.itemStyle?.color || CHART_COLORS[0];
    return {
      type: "line",
      ...s,
      smooth: s.smooth ?? props.smooth,
      showSymbol: false,
      areaStyle: s.area
        ? {
            opacity: 0.2,
            color: {
              type: "linear",
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color },
                { offset: 1, color: "rgba(37, 99, 235, 0.02)" },
              ],
            },
          }
        : undefined,
    };
  }),
}));

const { elRef } = useEChart(option);
</script>

<template>
  <div ref="elRef" class="w-full" :style="{ height }" role="img" :aria-label="title || 'Line chart'" />
</template>
