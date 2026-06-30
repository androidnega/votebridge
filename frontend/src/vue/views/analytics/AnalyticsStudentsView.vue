<script setup>
import { computed, onMounted } from "vue";
import LineChart from "@/components/charts/LineChart.vue";
import PieChart from "@/components/charts/PieChart.vue";
import { analyticsNav } from "@/config/moduleNav";
import { LoadingSkeleton, ModuleNav, PageHeader, VAlert, VCard } from "@/components/ui";
import { useAnalyticsStore } from "@/stores/analytics";

const store = useAnalyticsStore();
const loginTrend = computed(() => store.students?.login_trends || []);
const deviceItems = computed(() =>
  (store.students?.device_types || []).map((d) => ({ name: d.device_type || "unknown", value: d.count }))
);

onMounted(() => store.fetchStudents().catch(() => {}));
</script>

<template>
  <div class="vb-page">
    <PageHeader title="Student Analytics" :breadcrumbs="[{ label: 'Analytics', to: '/dashboard/analytics' }, { label: 'Students' }]" />
    <ModuleNav :items="analyticsNav" />
    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>
    <LoadingSkeleton v-if="store.loading && !store.students" variant="list" :rows="4" />
    <div v-else class="grid grid-cols-1 gap-4 lg:grid-cols-2">
      <VCard title="Login trends">
        <LineChart :labels="loginTrend.map((p) => p.label)" :series="[{ name: 'Logins', data: loginTrend.map((p) => p.value), area: true }]" />
      </VCard>
      <VCard title="Device types"><PieChart :items="deviceItems" /></VCard>
    </div>
  </div>
</template>
