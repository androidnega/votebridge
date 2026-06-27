<script setup>
import { computed } from "vue";
import { useEChart } from "./useEChart";

const props = defineProps({
  title: String,
  value: { type: Number, default: 0 },
  max: { type: Number, default: 100 },
  height: { type: String, default: "220px" },
});

const option = computed(() => ({
  series: [
    {
      type: "gauge",
      min: 0,
      max: props.max,
      progress: { show: true, width: 12 },
      axisLine: { lineStyle: { width: 12, color: [[1, "#E2E8F0"]] } },
      axisTick: { show: false },
      splitLine: { show: false },
      axisLabel: { show: false },
      pointer: { show: false },
      detail: {
        valueAnimation: true,
        formatter: "{value}%",
        fontSize: 24,
        color: "#1E3A6E",
        offsetCenter: [0, 0],
      },
      data: [{ value: props.value }],
      itemStyle: { color: "#1E3A6E" },
    },
  ],
}));

const { elRef } = useEChart(option);
</script>

<template>
  <div ref="elRef" class="w-full" :style="{ height }" role="img" :aria-label="title || 'Gauge chart'" />
</template>
