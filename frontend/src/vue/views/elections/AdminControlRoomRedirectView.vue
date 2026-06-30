<script setup>
import { onMounted } from "vue";
import { useRouter } from "vue-router";
import { LoadingSkeleton } from "@/components/ui";
import { useDashboardStore } from "@/stores/dashboard";

const router = useRouter();
const dashboardStore = useDashboardStore();

onMounted(async () => {
  if (!dashboardStore.adminOverview) {
    await dashboardStore.fetchAdminDashboard().catch(() => {});
  }

  const active = dashboardStore.openElectionsList.find((row) =>
    ["open", "paused"].includes(row.status || row.election_status)
  );
  const uuid =
    active?.uuid ||
    dashboardStore.adminOverview?.primary_election?.uuid ||
    dashboardStore.openElectionsList[0]?.uuid;

  if (uuid) {
    router.replace(`/dashboard/elections/${uuid}/monitor`);
    return;
  }
  router.replace("/dashboard/elections");
});
</script>

<template>
  <LoadingSkeleton variant="card" :rows="3" />
</template>
