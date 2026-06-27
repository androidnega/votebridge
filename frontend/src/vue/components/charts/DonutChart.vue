<script setup>
import PieChart from "@/components/charts/PieChart.vue";

defineProps({ donut: { type: Boolean, default: false } });
</script>

<template>
  <PieChart v-bind="$attrs" :donut="donut" />
</template>
