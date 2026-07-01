import { computed, onMounted, onUnmounted } from "vue";
import { storeToRefs } from "pinia";
import { useDashboardStore } from "@/stores/dashboard";

/**
 * Connects the role-scoped dashboard WebSocket feed and exposes live status.
 */
export function useDashboardRealtime(scope = "admin") {
  const dashboardStore = useDashboardStore();
  const { realtimeStatus, realtimeLabel, activityFeed, isRealtimeLive } =
    storeToRefs(dashboardStore);

  onMounted(() => {
    if (import.meta.env.VITE_ENABLE_REALTIME === "false") {
      return;
    }
    dashboardStore.connectRealtime(scope);
  });

  onUnmounted(() => {
    dashboardStore.disconnectRealtime();
  });

  return {
    status: realtimeStatus,
    label: realtimeLabel,
    isLive: isRealtimeLive,
    activityFeed,
    isPlaceholder: computed(() => false),
  };
}
