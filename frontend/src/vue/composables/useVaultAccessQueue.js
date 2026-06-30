import { ref } from "vue";
import { strongroomApi } from "@/api/strongroom";

/**
 * Aggregates pending vault access requests across closed elections (UI-only; per-election API).
 */
export function useVaultAccessQueue() {
  const pendingRequests = ref([]);
  const loading = ref(false);
  const error = ref(null);

  async function loadPendingRequests(results = []) {
    loading.value = true;
    error.value = null;
    try {
      const elections = results.length
        ? results.filter((row) => ["closed", "archived"].includes(row.election_status))
        : await strongroomApi.list().catch(() => []);

      const collected = [];
      const targets = elections.slice(0, 40);

      await Promise.all(
        targets.map(async (election) => {
          const electionUuid = election.election_uuid || election.uuid;
          const electionTitle = election.election_title || election.title;
          const requests = await strongroomApi.listAccessRequests(electionUuid).catch(() => []);
          for (const request of requests) {
            if (request.status === "pending") {
              collected.push({
                ...request,
                election_uuid: electionUuid,
                election_title: electionTitle,
              });
            }
          }
        })
      );

      collected.sort((a, b) => new Date(b.requested_at || 0) - new Date(a.requested_at || 0));
      pendingRequests.value = collected;
      return collected;
    } catch (err) {
      error.value = err?.message || "Failed to load vault access requests.";
      pendingRequests.value = [];
      throw err;
    } finally {
      loading.value = false;
    }
  }

  return {
    pendingRequests,
    loading,
    error,
    loadPendingRequests,
  };
}
