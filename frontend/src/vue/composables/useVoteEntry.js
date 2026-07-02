import { ref } from "vue";
import { useRouter } from "vue-router";
import { useVotingStore } from "@/stores/voting";

function isSvtAlreadyActiveError(message = "") {
  return String(message).toLowerCase().includes("already active");
}

export function useVoteEntry() {
  const router = useRouter();
  const votingStore = useVotingStore();
  const enteringElectionUuid = ref(null);
  const entryError = ref(null);

  async function goToPresenceOrBallot(electionUuid) {
    await votingStore.fetchPresenceStatus(electionUuid);
    if (votingStore.needsPresenceCapture) {
      router.push(`/dashboard/vote/presence/${electionUuid}`);
      return;
    }
    router.push(`/dashboard/elections/${electionUuid}/vote`);
  }

  async function enterVoteFlow(electionUuid) {
    if (!electionUuid || enteringElectionUuid.value) return;
    enteringElectionUuid.value = electionUuid;
    entryError.value = null;

    try {
      votingStore.resetSvtMemory();
      await votingStore.fetchVotingAccess(electionUuid);
      votingStore.restoreSvtSession(electionUuid);

      if (votingStore.svtAccess?.has_submitted_ballot) {
        router.push(`/dashboard/elections/${electionUuid}/confirmation`);
        return;
      }

      if (votingStore.hasValidatedBallotSession) {
        await goToPresenceOrBallot(electionUuid);
        return;
      }

      if (votingStore.tokenCode) {
        try {
          await votingStore.ensureSvtReadyForBallot(electionUuid);
          await goToPresenceOrBallot(electionUuid);
          return;
        } catch {
          if (isSvtAlreadyActiveError(votingStore.error)) {
            await goToPresenceOrBallot(electionUuid);
            return;
          }
          votingStore.clearElectionSvtState(electionUuid);
          entryError.value =
            votingStore.error ||
            "This voting token does not belong to this election. Enter the correct code.";
        }
      }

      if (votingStore.svtStatus === "issued" && votingStore.canRequestSvt === false) {
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
      enteringElectionUuid.value = null;
    }
  }

  return {
    enteringElectionUuid,
    entryError,
    enterVoteFlow,
    goToPresenceOrBallot,
  };
}
