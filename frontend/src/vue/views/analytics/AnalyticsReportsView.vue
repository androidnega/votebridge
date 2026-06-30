<script setup>
import { ref } from "vue";
import { analyticsNav } from "@/config/moduleNav";
import { useToast } from "@/composables/useToast";
import { ModuleNav, PageHeader, VAlert, VButton, VCard } from "@/components/ui";
import { useAnalyticsStore } from "@/stores/analytics";

const store = useAnalyticsStore();
const toast = useToast();
const reportType = ref("institution");
const format = ref("json");
const types = ["election", "participation", "security", "fraud", "operations", "communication", "strongroom", "institution"];
const formats = ["json", "csv", "excel", "pdf"];

async function exportReport() {
  try {
    const data = await store.fetchReport(reportType.value, format.value);
    if (format.value === "csv" && data.content) {
      const blob = new Blob([data.content], { type: "text/csv" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = data.filename || `report.${format.value}`;
      a.click();
      URL.revokeObjectURL(url);
    }
    toast.success("Report generated.");
  } catch {
    toast.error(store.error || "Export failed.");
  }
}
</script>

<template>
  <div class="vb-page">
    <PageHeader title="Analytics Reports" subtitle="Export institutional intelligence reports." :breadcrumbs="[{ label: 'Analytics', to: '/dashboard/analytics' }, { label: 'Reports' }]" />
    <ModuleNav :items="analyticsNav" />
    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>
    <VCard title="Generate report">
      <form class="grid grid-cols-1 gap-4 md:grid-cols-2" @submit.prevent="exportReport">
        <label class="text-sm">
          Report type
          <select v-model="reportType" class="mt-1 w-full rounded-input border border-border px-3 py-2">
            <option v-for="t in types" :key="t" :value="t">{{ t }}</option>
          </select>
        </label>
        <label class="text-sm">
          Format
          <select v-model="format" class="mt-1 w-full rounded-input border border-border px-3 py-2">
            <option v-for="f in formats" :key="f" :value="f">{{ f }}</option>
          </select>
        </label>
        <div class="md:col-span-2"><VButton type="submit" variant="primary">Export report</VButton></div>
      </form>
    </VCard>
  </div>
</template>
