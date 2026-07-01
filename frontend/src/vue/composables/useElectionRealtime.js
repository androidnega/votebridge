import { onUnmounted, unref, watch } from "vue";
import { storeToRefs } from "pinia";
import { useVotingStore } from "@/stores/voting";

export function useElectionRealtime(electionUuidRef) {
  const votingStore = useVotingStore();
  const { electionStatus, realtimeStatus } = storeToRefs(votingStore);

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
    electionStatus,
    realtimeStatus,
  };
}
