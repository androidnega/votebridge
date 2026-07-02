import { defineStore } from "pinia";
import { electionsApi, securityApi, votingApi } from "@/api";
import { extractApiError } from "@/api/helpers";
import { applySelection, skipPositionSelection } from "@/utils/ballotSelection";
import { normalizeSvtToken } from "@/utils/svtToken";
import realtimeService from "@/services/websocket";

const CONFIRMATION_STORAGE_PREFIX = "vb_ballot_confirmation_";
const BALLOT_SELECTIONS_PREFIX = "vb_ballot_selections_";
const BALLOT_STEP_PREFIX = "vb_ballot_step_";
const SVT_TOKEN_PREFIX = "vb_svt_token_";
const SVT_SESSION_PREFIX = "vb_svt_session_";

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
    svtAccess: null,
    svtStatus: null,
    canRequestSvt: true,
    maskedPhone: "",
    resendAvailableAt: null,
    selections: {},
    currentStep: 1,
    electionStatus: null,
    confirmationStatus: null,
    ballotSubmitted: false,
    validating: false,
    requestingSvt: false,
    resendingSvt: false,
    realtimeStatus: "disconnected",
    electionRealtimeUuid: null,
    loading: false,
    submitting: false,
    presenceStatus: null,
    presenceSubmitting: false,
    error: null,
  }),

  getters: {
    sortedPositions: (state) => sortPositions(state.ballot?.positions || []),
    positionStepCount(state) {
      return this.sortedPositions.length;
    },
    totalWizardSteps(state) {
      const count = this.sortedPositions.length;
      return count > 0 ? count + 1 : 1;
    },
    isReviewStep(state) {
      return state.currentStep === this.totalWizardSteps;
    },
    currentPosition(state) {
      if (this.isReviewStep) return null;
      return this.sortedPositions[state.currentStep - 1] || null;
    },
    progressPercent(state) {
      const total = this.totalWizardSteps;
      if (total <= 1) return 100;
      return Math.round((state.currentStep / total) * 100);
    },
    reviewSelections(state) {
      return this.sortedPositions.map((position) => ({
        position,
        candidates: (state.selections[position.uuid] || [])
          .map((uuid) => position.candidates?.find((c) => c.uuid === uuid))
          .filter(Boolean),
      }));
    },
    skippedCount(state) {
      return this.reviewSelections.filter((item) => !item.candidates.length).length;
    },
    selectedCount(state) {
      return this.reviewSelections.filter((item) => item.candidates.length).length;
    },
    canSubmitBallot(state) {
      return this.selectedCount >= 1 && state.svtSession?.status === "validated";
    },
    hasActiveSvt(state) {
      return state.svtStatus === "issued" || state.svtStatus === "validated";
    },
    isFirstBallotStep(state) {
      return state.currentStep <= 1 && !this.isReviewStep;
    },
    isLastPositionStep(state) {
      return !this.isReviewStep && state.currentStep === this.sortedPositions.length;
    },
    ballotSessionActive(state) {
      return state.ballot?.ballot_session_active || state.svtSession?.status === "validated";
    },
    hasValidatedBallotSession(state) {
      return (
        state.svtStatus === "validated" ||
        state.svtSession?.status === "validated" ||
        state.svtAccess?.svt_status === "validated" ||
        state.ballot?.ballot_session_active === true
      );
    },
    needsPresenceCapture(state) {
      if (!state.presenceStatus?.presence_required) return false;
      return !state.presenceStatus?.presence_captured;
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
        this.svtStatus = this.ballot.svt_status || null;
        this.canRequestSvt = this.ballot.can_request_svt !== false;
        this.maskedPhone = this.ballot.masked_phone || this.maskedPhone;
        this.restoreBallotState(electionUuid);
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

    async fetchVotingAccess(electionUuid) {
      this.svtAccess = await securityApi.getVotingAccess(electionUuid);
      this.svtStatus = this.svtAccess.svt_status;
      this.canRequestSvt = this.svtAccess.can_request_svt;
      this.maskedPhone = this.svtAccess.masked_phone || this.maskedPhone;
      this.resendAvailableAt = this.svtAccess.resend_available_at;
      if (this.svtAccess.has_submitted_ballot) {
        this.ballotSubmitted = true;
        this.confirmationStatus = "recorded";
      }
      return this.svtAccess;
    },

    async requestSvt(electionUuid) {
      this.requestingSvt = true;
      this.error = null;
      try {
        this.svtIssued = await securityApi.requestSvt(electionUuid);
        this.svtStatus = this.svtIssued.status || "issued";
        this.canRequestSvt = false;
        this.maskedPhone = this.svtIssued.masked_phone || this.maskedPhone;
        this.resendAvailableAt = this.svtIssued.resend_available_at;
        return this.svtIssued;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.requestingSvt = false;
      }
    },

    async resendSvt(electionUuid) {
      this.resendingSvt = true;
      this.error = null;
      try {
        this.svtIssued = await securityApi.resendSvt(electionUuid);
        this.svtStatus = this.svtIssued.status || "issued";
        this.resendAvailableAt = this.svtIssued.resend_available_at;
        return this.svtIssued;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.resendingSvt = false;
      }
    },

    async validateSvt(electionUuid, tokenCode = this.tokenCode) {
      this.validating = true;
      this.error = null;
      try {
        this.tokenCode = normalizeSvtToken(tokenCode);
        if (!this.tokenCode) {
          throw new Error("Invalid Secure Voting Token.");
        }
        this.svtSession = await securityApi.validateSvt(electionUuid, this.tokenCode);
        this.svtStatus = this.svtSession.status || "validated";
        this.canRequestSvt = false;
        this.persistSvtSession(electionUuid);
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

    selectCandidate(position, candidateUuid, electionUuid) {
      const next = applySelection(
        position,
        this.selections[position.uuid] || [],
        candidateUuid
      );
      this.setSelection(position.uuid, next);
      if (electionUuid) {
        this.persistBallotState(electionUuid);
      }
    },

    skipPosition(position, electionUuid) {
      this.setSelection(position.uuid, skipPositionSelection());
      if (electionUuid) {
        this.persistBallotState(electionUuid);
      }
    },

    toggleCandidate(position, candidateUuid, electionUuid = null) {
      this.selectCandidate(position, candidateUuid, electionUuid);
    },

    continueLater(electionUuid) {
      this.persistBallotState(electionUuid);
      this.persistSvtSession(electionUuid);
    },

    nextStep(electionUuid) {
      if (this.currentStep < this.totalWizardSteps) {
        this.currentStep += 1;
        this.persistBallotState(electionUuid);
      }
    },

    prevStep(electionUuid) {
      if (this.currentStep > 1) {
        this.currentStep -= 1;
        this.persistBallotState(electionUuid);
      }
    },

    goToStep(step, electionUuid) {
      if (step >= 1 && step <= this.totalWizardSteps) {
        this.currentStep = step;
        this.persistBallotState(electionUuid);
      }
    },

    goToPositionStep(positionUuid, electionUuid) {
      const index = this.sortedPositions.findIndex((p) => p.uuid === positionUuid);
      if (index >= 0) {
        this.goToStep(index + 1, electionUuid);
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
        this.clearBallotState(electionUuid);
        this.ballotSubmitted = true;
        this.confirmationStatus = "recorded";
        this.consumeSvtSession(electionUuid);
        return this.lastConfirmation;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.submitting = false;
      }
    },

    consumeSvtSession(electionUuid) {
      this.tokenCode = "";
      this.svtSession = null;
      this.svtIssued = null;
      this.svtStatus = "used";
      this.canRequestSvt = true;
      if (electionUuid) {
        sessionStorage.removeItem(`${SVT_TOKEN_PREFIX}${electionUuid}`);
        sessionStorage.removeItem(`${SVT_SESSION_PREFIX}${electionUuid}`);
      }
    },

    clearElectionSvtState(electionUuid) {
      this.tokenCode = "";
      this.svtSession = null;
      this.svtIssued = null;
      if (electionUuid) {
        sessionStorage.removeItem(`${SVT_TOKEN_PREFIX}${electionUuid}`);
        sessionStorage.removeItem(`${SVT_SESSION_PREFIX}${electionUuid}`);
      }
    },

    resetSvtMemory() {
      this.tokenCode = "";
      this.svtSession = null;
      this.svtIssued = null;
    },

    restoreSvtSession(electionUuid) {
      this.tokenCode = "";
      this.svtSession = null;
      const token = sessionStorage.getItem(`${SVT_TOKEN_PREFIX}${electionUuid}`);
      const raw = sessionStorage.getItem(`${SVT_SESSION_PREFIX}${electionUuid}`);
      if (token) this.tokenCode = token;
      if (raw) {
        try {
          this.svtSession = JSON.parse(raw);
          if (this.svtSession?.status) {
            this.svtStatus = this.svtSession.status;
          }
        } catch {
          /* ignore */
        }
      }
    },

    async ensureSvtReadyForBallot(electionUuid) {
      this.restoreSvtSession(electionUuid);
      if (this.hasValidatedBallotSession) {
        return true;
      }
      if (!this.tokenCode) {
        return false;
      }
      await this.validateSvt(electionUuid, this.tokenCode);
      return true;
    },

    persistSvtSession(electionUuid) {
      sessionStorage.setItem(`${SVT_TOKEN_PREFIX}${electionUuid}`, this.tokenCode);
      sessionStorage.setItem(
        `${SVT_SESSION_PREFIX}${electionUuid}`,
        JSON.stringify(this.svtSession || {})
      );
    },

    persistBallotState(electionUuid) {
      sessionStorage.setItem(
        `${BALLOT_SELECTIONS_PREFIX}${electionUuid}`,
        JSON.stringify(this.selections)
      );
      sessionStorage.setItem(`${BALLOT_STEP_PREFIX}${electionUuid}`, String(this.currentStep));
    },

    restoreBallotState(electionUuid) {
      const rawSelections = sessionStorage.getItem(`${BALLOT_SELECTIONS_PREFIX}${electionUuid}`);
      const rawStep = sessionStorage.getItem(`${BALLOT_STEP_PREFIX}${electionUuid}`);
      if (rawSelections) {
        try {
          this.selections = { ...emptySelections(this.ballot?.positions), ...JSON.parse(rawSelections) };
        } catch {
          this.selections = emptySelections(this.ballot?.positions);
        }
      }
      if (rawStep) {
        const step = Number.parseInt(rawStep, 10);
        if (step >= 1 && step <= this.totalWizardSteps) {
          this.currentStep = step;
        }
      }
      this.restoreSvtSession(electionUuid);
    },

    clearBallotState(electionUuid) {
      sessionStorage.removeItem(`${BALLOT_SELECTIONS_PREFIX}${electionUuid}`);
      sessionStorage.removeItem(`${BALLOT_STEP_PREFIX}${electionUuid}`);
      this.clearWizardSelections();
    },

    async fetchPresenceStatus(electionUuid) {
      this.error = null;
      try {
        this.presenceStatus = await votingApi.getPresenceStatus(electionUuid);
        return this.presenceStatus;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      }
    },

    async submitPresenceCapture(electionUuid, imageBlob) {
      this.presenceSubmitting = true;
      this.error = null;
      try {
        this.restoreSvtSession(electionUuid);
        if (!this.tokenCode) {
          throw new Error("Your voting session has expired. Verify your code again.");
        }
        const formData = new FormData();
        formData.append("token_code", this.tokenCode);
        formData.append("channel", "web");
        formData.append("image", imageBlob, "presence.jpg");
        const result = await votingApi.submitPresenceCapture(electionUuid, formData);
        this.presenceStatus = {
          ...(this.presenceStatus || {}),
          presence_required: true,
          presence_captured: true,
          captured_at: result.captured_at,
        };
        return result;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.presenceSubmitting = false;
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
        confirmation_reference: confirmation.confirmation_reference,
        positions_skipped: confirmation.positions_skipped,
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
      this.currentStep = 1;
    },

    resetWizard(electionUuid) {
      this.error = null;
      if (electionUuid) {
        this.clearBallotState(electionUuid);
      } else {
        this.clearWizardSelections();
      }
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
        this.svtStatus = data.status;
      }
    },

    clearBallot() {
      this.ballot = null;
      this.previewPositions = [];
      this.previewCandidates = [];
    },
  },
});
