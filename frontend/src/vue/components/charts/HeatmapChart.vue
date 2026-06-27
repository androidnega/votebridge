<script setup>
import { computed } from "vue";
import { useEChart } from "./useEChart";

const props = defineProps({
  title: String,
  points: { type: Array, default: () => [] },
  height: { type: String, default: "320px" },
});

const option = computed(() => ({
  tooltip: { position: "top" },
  grid: { left: 80, right: 24, top: 24, bottom: 48 },
  xAxis: {
    type: "category",
    data: [...new Set(props.points.map((p) => p.x))],
    splitArea: { show: true },
  },
  yAxis: {
    type: "category",
    data: [...new Set(props.points.map((p) => p.y))],
    splitArea: { show: true },
  },
  visualMap: {
    min: 0,
    max: 100,
    calculable: false,
    orient: "horizontal",
    left: "center",
    bottom: 0,
    inRange: { color: ["#F5F7F9", "#1E3A6E"] },
  },
  series: [
    {
      type: "heatmap",
      data: props.points.map((p) => [p.x, p.y, p.value]),
      label: { show: false },
    },
  ],
}));

const { elRef } = useEChart(option);
</script>

<template>
  <div ref="elRef" class="w-full" :style="{ height }" role="img" :aria-label="title || 'Heatmap chart'" />
</template>
