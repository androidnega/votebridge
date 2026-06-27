import { onUnmounted, unref, watch } from "vue";
import { useVotingStore } from "@/stores/voting";

export function useElectionRealtime(electionUuidRef) {
  const votingStore = useVotingStore();

  watch(
    () => unref(electionUuidRef),
    (uuid, _, onCleanup) => {
      if (uuid) {
        votingStore.connectElectionRealtime(uuid);
      }
      onCleanup(() => {
        votingStore.disconnectElectionRealtime();
      });
    },
    { immediate: true }
  );

  return {
    electionStatus: votingStore.electionStatus,
    realtimeStatus: votingStore.realtimeStatus,
  };
}
