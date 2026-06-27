<script setup>
import LineChart from "./LineChart.vue";

defineProps({ title: String, labels: Array, series: Array, height: String });
</script>

<template>
  <LineChart v-bind="$attrs" :series="(series || []).map((s) => ({ ...s, area: true }))" />
</template>
