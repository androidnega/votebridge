<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";
import { PageHeader } from "@/components/ui";
import { useElectionStore } from "@/stores/election";

const props = defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: "" },
});

const route = useRoute();
const electionStore = useElectionStore();

const electionUuid = computed(() => route.params.uuid);
const electionTitle = computed(() => electionStore.currentElection?.title || "Election");

const breadcrumbs = computed(() => [
  { label: "Election workspace", to: "/dashboard/elections" },
  { label: electionTitle.value, to: `/dashboard/elections/${electionUuid.value}` },
  { label: props.title },
]);
</script>

<template>
  <div class="vb-page space-y-section">
    <PageHeader :title="title" :subtitle="subtitle" :breadcrumbs="breadcrumbs" />
    <slot />
  </div>
</template>
