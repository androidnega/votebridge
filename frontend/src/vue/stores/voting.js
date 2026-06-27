import { defineStore } from "pinia";
import { electionsApi, securityApi, votingApi } from "@/api";
import { extractApiError } from "@/api/helpers";
import realtimeService from "@/services/websocket";

const CONFIRMATION_STORAGE_PREFIX = "vb_ballot_confirmation_";

function sortPositions(positions = []) {
  return [...positions].sort(
    (a, b) => (a.display_order ?? 0) - (b.display_order ?? 0)
  );
}

function emptySelections(positions = []) {
  return positions.reduce((acc, position) => {
    acc[position.uuid] = [];
    return acc;
  }, {});
}

export const useVotingStore = defineStore("voting", {
  state: () => ({
    ballot: null,
    myVotes: [],
    lastConfirmation: null,
    previewPositions: [],
    previewCandidates: [],
    tokenCode: "",
    svtSession: null,
    svtIssued: null,
    selections: {},
    currentStep: 0,
    electionStatus: null,
    confirmationStatus: null,
    ballotSubmitted: false,
    validating: false,
    requestingSvt: false,
    realtimeStatus: "disconnected",
    electionRealtimeUuid: null,
    loading: false,
    submitting: false,
    error: null,
  }),

  getters: {
    sortedPositions: (state) => sortPositions(state.ballot?.positions || []),
    totalWizardSteps: (state) => {
      const positionCount = sortPositions(state.ballot?.positions || []).length;
      return positionCount > 0 ? positionCount + 2 : 2;
    },
    isSvtStep: (state) => state.currentStep === 0,
    isReviewStep(state) {
      const positionCount = this.sortedPositions.length;
      return state.currentStep === positionCount + 1;
    },
    currentPosition(state) {
      if (this.isSvtStep || this.isReviewStep) return null;
      return this.sortedPositions[state.currentStep - 1] || null;
    },
    canProceed(state) {
      if (this.isSvtStep) return Boolean(state.svtSession?.status === "validated");
      if (this.isReviewStep) return this.allPositionsComplete;
      const position = this.currentPosition;
      if (!position) return false;
      const selected = state.selections[position.uuid] || [];
      return selected.length >= 1 && selected.length <= (position.max_votes_allowed || 1);
    },
    allPositionsComplete(state) {
      return this.sortedPositions.every((position) => {
        const selected = state.selections[position.uuid] || [];
        return selected.length >= 1 && selected.length <= (position.max_votes_allowed || 1);
      });
    },
    progressPercent(state) {
      const total = this.totalWizardSteps;
      if (total <= 1) return 0;
      return Math.round((state.currentStep / (total - 1)) * 100);
    },
    reviewSelections(state) {
      return this.sortedPositions.map((position) => ({
        position,
        candidates: (state.selections[position.uuid] || [])
          .map((uuid) => position.candidates?.find((c) => c.uuid === uuid))
          .filter(Boolean),
      }));
    },
  },

  actions: {
    async fetchBallot(electionUuid) {
      this.loading = true;
      this.error = null;
      try {
        this.ballot = await votingApi.getBallot(electionUuid);
        this.selections = emptySelections(this.ballot.positions);
        this.previewPositions = sortPositions(this.ballot.positions);
        return this.ballot;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchPreviewData(electionUuid, { isAdmin = false } = {}) {
      if (isAdmin) {
        try {
          const [positions, candidates] = await Promise.all([
            electionsApi.listPositions(electionUuid, { page_size: 50, is_active: true }),
            electionsApi.listCandidates(electionUuid, { page_size: 100 }),
          ]);
          this.previewPositions = sortPositions(positions.items);
          this.previewCandidates = candidates.items;
        } catch (error) {
          this.error = extractApiError(error);
        }
        return;
      }

      try {
        await this.fetchBallot(electionUuid);
        this.previewCandidates = (this.ballot?.positions || []).flatMap(
          (position) => position.candidates || []
        );
      } catch {
        this.previewPositions = [];
        this.previewCandidates = [];
      }
    },

    async requestSvt(electionUuid) {
      this.requestingSvt = true;
      this.error = null;
      try {
        this.svtIssued = await securityApi.requestSvt(electionUuid);
        this.tokenCode = this.svtIssued.token_code || "";
        return this.svtIssued;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.requestingSvt = false;
      }
    },

    async validateSvt(electionUuid, tokenCode = this.tokenCode) {
      this.validating = true;
      this.error = null;
      try {
        this.tokenCode = tokenCode.trim();
        this.svtSession = await securityApi.validateSvt(electionUuid, this.tokenCode);
        return this.svtSession;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.validating = false;
      }
    },

    setSelection(positionUuid, candidateUuids) {
      this.selections = {
        ...this.selections,
        [positionUuid]: [...candidateUuids],
      };
    },

    toggleCandidate(position, candidateUuid) {
      const current = [...(this.selections[position.uuid] || [])];
      const isMulti = position.choice_type === "multi";
      const max = position.max_votes_allowed || 1;

      if (isMulti) {
        const index = current.indexOf(candidateUuid);
        if (index >= 0) {
          current.splice(index, 1);
        } else if (current.length < max) {
          current.push(candidateUuid);
        }
      } else {
        current.length = 0;
        current.push(candidateUuid);
      }

      this.setSelection(position.uuid, current);
    },

    nextStep() {
      if (this.currentStep < this.totalWizardSteps - 1) {
        this.currentStep += 1;
      }
    },

    prevStep() {
      if (this.currentStep > 0) {
        this.currentStep -= 1;
      }
    },

    goToStep(step) {
      if (step >= 0 && step < this.totalWizardSteps) {
        this.currentStep = step;
      }
    },

    async submitBallot(electionUuid) {
      this.submitting = true;
      this.error = null;
      try {
        const payload = {
          token_code: this.tokenCode,
          channel_name: "web",
          selections: this.sortedPositions.map((position) => ({
            position_uuid: position.uuid,
            candidate_uuids: this.selections[position.uuid] || [],
          })),
        };
        this.lastConfirmation = await votingApi.submitBallot(electionUuid, payload);
        this.persistConfirmation(electionUuid, this.lastConfirmation);
        this.clearWizardSelections();
        this.ballotSubmitted = true;
        this.confirmationStatus = "recorded";
        return this.lastConfirmation;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.submitting = false;
      }
    },

    async fetchMyVotes(electionUuid) {
      this.loading = true;
      this.error = null;
      try {
        this.myVotes = await votingApi.listMyVotes(electionUuid);
        return this.myVotes;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async verifySubmittedBallot(tokenCode = this.tokenCode) {
      try {
        return await securityApi.verifySvt(tokenCode);
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      }
    },

    persistConfirmation(electionUuid, confirmation) {
      const safe = {
        election_uuid: confirmation.election_uuid,
        election_title: confirmation.election_title,
        positions_completed: confirmation.positions_completed,
        positions_count: confirmation.positions_count,
        votes_count: confirmation.votes_count,
        timestamp: confirmation.timestamp,
        message: confirmation.message,
      };
      sessionStorage.setItem(
        `${CONFIRMATION_STORAGE_PREFIX}${electionUuid}`,
        JSON.stringify(safe)
      );
      this.lastConfirmation = safe;
    },

    loadConfirmation(electionUuid) {
      if (this.lastConfirmation?.election_uuid === electionUuid) {
        return this.lastConfirmation;
      }
      const raw = sessionStorage.getItem(`${CONFIRMATION_STORAGE_PREFIX}${electionUuid}`);
      if (!raw) return null;
      try {
        this.lastConfirmation = JSON.parse(raw);
        return this.lastConfirmation;
      } catch {
        return null;
      }
    },

    clearWizardSelections() {
      this.selections = emptySelections(this.ballot?.positions || []);
    },

    resetWizard() {
      this.currentStep = 0;
      this.tokenCode = "";
      this.svtSession = null;
      this.svtIssued = null;
      this.error = null;
      this.clearWizardSelections();
    },

    connectElectionRealtime(electionUuid) {
      this.electionRealtimeUuid = electionUuid;
      this.realtimeStatus = "connecting";
      realtimeService.connectElection(electionUuid, {
        onStatusChange: (status) => {
          this.realtimeStatus = status;
        },
        onMessage: (message) => {
          this.handleElectionRealtimeMessage(message);
        },
      });
    },

    disconnectElectionRealtime() {
      if (this.electionRealtimeUuid) {
        realtimeService.disconnect(`election-${this.electionRealtimeUuid}`);
        this.electionRealtimeUuid = null;
      }
      this.realtimeStatus = "disconnected";
    },

    handleElectionRealtimeMessage(message) {
      const { event, data } = message;
      if (!data) return;

      if (event === "dashboard_stats") {
        if (data.election_status) this.electionStatus = data.election_status;
        if (data.confirmation_status) this.confirmationStatus = data.confirmation_status;
        if (data.ballot_submitted !== undefined) this.ballotSubmitted = data.ballot_submitted;
        return;
      }

      if (data.election_status) {
        this.electionStatus = data.election_status;
      }

      if (event === "ballot_submitted" && data.confirmation_status) {
        this.confirmationStatus = data.confirmation_status;
        this.ballotSubmitted = true;
      }

      if (["svt_issued", "svt_validated", "svt_consumed"].includes(event) && data.status) {
        if (this.svtSession) {
          this.svtSession = { ...this.svtSession, status: data.status };
        }
      }
    },

    clearBallot() {
      this.ballot = null;
      this.previewPositions = [];
      this.previewCandidates = [];
      this.resetWizard();
    },
  },
});
