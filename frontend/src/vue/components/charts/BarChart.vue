<script setup>
import { computed } from "vue";
import { CHART_COLORS, useEChart } from "./useEChart";

const props = defineProps({
  title: String,
  labels: { type: Array, default: () => [] },
  values: { type: Array, default: () => [] },
  horizontal: Boolean,
  percent: Boolean,
  height: { type: String, default: "280px" },
});

const gridLeft = computed(() => {
  if (!props.horizontal || !props.labels.length) return 40;
  const longest = Math.max(...props.labels.map((label) => String(label).length), 12);
  return Math.min(240, Math.max(128, longest * 7));
});

const chartHeight = computed(() => {
  if (!props.horizontal) return props.height;
  const rows = Math.max(props.labels.length, 1);
  const minHeight = 56 * rows + 48;
  return `${Math.max(minHeight, parseInt(props.height, 10) || 280)}px`;
});

const option = computed(() => {
  const valueAxis = {
    type: "value",
    max: props.percent ? 100 : undefined,
    splitLine: { lineStyle: { color: "#E2E8F0" } },
    axisLabel: props.percent ? { formatter: "{value}%" } : undefined,
  };

  return {
    color: CHART_COLORS,
    title: props.title
      ? { text: props.title, left: 0, textStyle: { fontSize: 14, fontWeight: 600, color: "#0F172A" } }
      : undefined,
    tooltip: {
      trigger: "axis",
      axisPointer: { type: "shadow" },
      formatter: props.percent
        ? (params) => {
            const point = Array.isArray(params) ? params[0] : params;
            if (!point) return "";
            return `${point.name}<br/><strong>${point.value}%</strong> turnout`;
          }
        : undefined,
    },
    grid: {
      left: props.horizontal ? gridLeft.value : 40,
      right: 24,
      top: props.title ? 48 : 24,
      bottom: 32,
      containLabel: !props.horizontal,
    },
    xAxis: props.horizontal ? valueAxis : { type: "category", data: props.labels },
    yAxis: props.horizontal
      ? {
          type: "category",
          data: props.labels,
          axisLabel: { color: "#475569", fontSize: 12 },
        }
      : valueAxis,
    series: [
      {
        type: "bar",
        data: props.values,
        barMaxWidth: 28,
        itemStyle: {
          borderRadius: props.horizontal ? [0, 4, 4, 0] : [4, 4, 0, 0],
          color: CHART_COLORS[0],
        },
        label: props.percent
          ? {
              show: true,
              position: "right",
              formatter: "{c}%",
              color: "#475569",
              fontSize: 12,
            }
          : undefined,
      },
    ],
  };
});

const { elRef } = useEChart(option);
</script>

<template>
  <div
    ref="elRef"
    class="w-full"
    :style="{ height: chartHeight }"
    role="img"
    :aria-label="title || 'Bar chart'"
  />
</template>
