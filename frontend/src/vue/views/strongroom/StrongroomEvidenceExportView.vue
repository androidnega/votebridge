<script setup>
import { useRouter } from "vue-router";
import { PageHeader, VCard, VButton } from "@/components/ui";

const router = useRouter();

const exports = [
  {
    title: "Analytics reports",
    description: "Download turnout, participation, and historical election reports.",
    to: "/reports/export",
  },
  {
    title: "Public verification",
    description: "Generate verification hashes for independent result checks.",
    to: "/verify",
  },
  {
    title: "Platform audit trail",
    description: "Export operational and security audit logs.",
    to: "/strongroom/audit",
  },
];
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="Evidence export"
      subtitle="Export certified records, reports, and verification artefacts."
      :breadcrumbs="[{ label: 'Strong room', to: '/strongroom' }, { label: 'Evidence export' }]"
    />

    <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
      <VCard v-for="item in exports" :key="item.title" :title="item.title">
        <p class="text-sm text-slate-600">{{ item.description }}</p>
        <VButton class="mt-4" variant="secondary" size="sm" @click="router.push(item.to)">
          Open
        </VButton>
      </VCard>
    </div>
  </div>
</template>
