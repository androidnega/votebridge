<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";
import { PageHeader } from "@/components/ui";
import { useElectionStore } from "@/stores/election";

const props = defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: "" },
  layout: {
    type: String,
    default: "default",
    validator: (value) => ["default", "list"].includes(value),
  },
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
  <div :class="layout === 'list' ? 'vb-page vb-page--list' : 'vb-page space-y-section'">
    <PageHeader
      class="shrink-0"
      :title="title"
      :subtitle="subtitle"
      :breadcrumbs="breadcrumbs"
    >
      <template v-if="$slots.actions" #actions>
        <slot name="actions" />
      </template>
    </PageHeader>
    <slot />
  </div>
</template>
