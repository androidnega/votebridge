<script setup>
import { onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { LoadingSkeleton } from "@/components/ui";
import { useDashboardStore } from "@/stores/dashboard";

const props = defineProps({
  section: { type: String, required: true },
});

const route = useRoute();
const router = useRouter();
const dashboardStore = useDashboardStore();

onMounted(async () => {
  if (!dashboardStore.adminOverview) {
    await dashboardStore.fetchAdminDashboard().catch(() => {});
  }

  const fromQuery = route.query.election;
  const primary =
    fromQuery ||
    dashboardStore.openElectionsList[0]?.uuid ||
    dashboardStore.adminOverview?.primary_election?.uuid;

  if (primary) {
    router.replace(`/dashboard/elections/${primary}/${props.section}`);
    return;
  }
  router.replace("/dashboard/elections");
});
</script>

<template>
  <LoadingSkeleton variant="card" :rows="3" />
</template>
