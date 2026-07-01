import { ref } from "vue";
import { useRouter } from "vue-router";
import { useVotingStore } from "@/stores/voting";

export function useVoteEntry() {
  const router = useRouter();
  const votingStore = useVotingStore();
  const entering = ref(false);
  const entryError = ref(null);

  function hasActiveBallotSession(electionUuid) {
    votingStore.restoreSvtSession(electionUuid);
    return (
      votingStore.svtStatus === "validated" ||
      votingStore.svtSession?.status === "validated"
    );
  }

  async function enterVoteFlow(electionUuid) {
    if (!electionUuid || entering.value) return;
    entering.value = true;
    entryError.value = null;

    try {
      await votingStore.fetchVotingAccess(electionUuid);

      if (votingStore.svtAccess?.has_submitted_ballot) {
        router.push(`/dashboard/elections/${electionUuid}/confirmation`);
        return;
      }

      if (hasActiveBallotSession(electionUuid) && votingStore.tokenCode) {
        router.push(`/dashboard/elections/${electionUuid}/vote`);
        return;
      }

      if (votingStore.svtStatus === "issued") {
        router.push(`/dashboard/vote/verify/${electionUuid}`);
        return;
      }

      if (votingStore.canRequestSvt) {
        await votingStore.requestSvt(electionUuid);
      }

      router.push(`/dashboard/vote/verify/${electionUuid}`);
    } catch (error) {
      entryError.value = votingStore.error || error.message || "Unable to start voting.";
    } finally {
      entering.value = false;
    }
  }

  return {
    entering,
    entryError,
    enterVoteFlow,
  };
}
