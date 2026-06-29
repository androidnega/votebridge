<script setup>
import { useRouter } from "vue-router";
import { ModuleNav, PageHeader, VCard, VButton } from "@/components/ui";
import { settingsNav } from "@/config/moduleNav";

const router = useRouter();

const channels = [
  {
    title: "Web voting",
    description: "Browser-based voting policies and channel availability.",
    to: "/settings/election-policies",
  },
  {
    title: "USSD voting",
    description: "Mobile USSD menu codes, session limits, and provider routing.",
    to: "/settings/ussd",
  },
  {
    title: "SMS notifications",
    description: "SMS delivery settings and notification templates.",
    to: "/settings/notifications",
  },
  {
    title: "Channel health",
    description: "Monitor USSD sessions, queues, and delivery performance.",
    to: "/ussd",
  },
  {
    title: "Provider testing",
    description: "Send test messages and validate communication providers.",
    to: "/communications/test",
  },
];
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="Voting channels"
      subtitle="Configure how students vote and receive election communications."
      :breadcrumbs="[{ label: 'Settings', to: '/settings' }, { label: 'Voting channels' }]"
    />

    <ModuleNav :items="settingsNav" />

    <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
      <VCard v-for="channel in channels" :key="channel.title" :title="channel.title">
        <p class="text-sm text-slate-600">{{ channel.description }}</p>
        <VButton class="mt-4" variant="secondary" size="sm" @click="router.push(channel.to)">
          Open
        </VButton>
      </VCard>
    </div>
  </div>
</template>
