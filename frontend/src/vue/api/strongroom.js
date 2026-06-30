import apiClient from "./client";
import { unwrapResponse } from "./helpers";

export const strongroomApi = {
  list() {
    return apiClient.get("/strongroom/elections/").then(unwrapResponse);
  },

  getDashboard(electionUuid) {
    return apiClient.get(`/strongroom/elections/${electionUuid}/dashboard/`).then(unwrapResponse);
  },

  getCustodyTimeline(electionUuid) {
    return apiClient.get(`/strongroom/elections/${electionUuid}/custody/`).then(unwrapResponse);
  },

  verifyIntegrity(electionUuid, tokens = {}) {
    return apiClient.post(`/strongroom/elections/${electionUuid}/verify/`, tokens).then(unwrapResponse);
  },

  lockElection(electionUuid) {
    return apiClient.post(`/strongroom/elections/${electionUuid}/lock/`).then(unwrapResponse);
  },

  publicVerify(electionUuid, verificationHash) {
    return apiClient
      .post("/strongroom/public/verify/", {
        election_uuid: electionUuid,
        verification_hash: verificationHash,
      })
      .then(unwrapResponse);
  },

  getCommittee(electionUuid) {
    return apiClient.get(`/strongroom/elections/${electionUuid}/committee/`).then(unwrapResponse);
  },

  saveCommittee(electionUuid, payload) {
    return apiClient.post(`/strongroom/elections/${electionUuid}/committee/`, payload).then(unwrapResponse);
  },

  submitCommittee(electionUuid) {
    return apiClient.post(`/strongroom/elections/${electionUuid}/committee/submit/`).then(unwrapResponse);
  },

  approveCommittee(electionUuid) {
    return apiClient.post(`/strongroom/elections/${electionUuid}/committee/approve/`).then(unwrapResponse);
  },

  listAccessRequests(electionUuid) {
    return apiClient.get(`/strongroom/elections/${electionUuid}/access-requests/`).then(unwrapResponse);
  },

  createAccessRequest(electionUuid, payload) {
    return apiClient.post(`/strongroom/elections/${electionUuid}/access-requests/`, payload).then(unwrapResponse);
  },

  reviewAccessRequest(electionUuid, requestUuid, action) {
    return apiClient
      .post(`/strongroom/elections/${electionUuid}/access-requests/${requestUuid}/review/`, { action })
      .then(unwrapResponse);
  },

  startVaultSession(electionUuid, accessRequestUuid) {
    return apiClient
      .post(`/strongroom/elections/${electionUuid}/vault-sessions/`, {
        access_request_uuid: accessRequestUuid,
      })
      .then(unwrapResponse);
  },

  getVaultSession(sessionUuid) {
    return apiClient.get(`/strongroom/vault-sessions/${sessionUuid}/`).then(unwrapResponse);
  },

  authenticateCustodian(sessionUuid, payload) {
    return apiClient
      .post(`/strongroom/vault-sessions/${sessionUuid}/authenticate/`, payload)
      .then(unwrapResponse);
  },

  getVaultEvidence(sessionUuid) {
    return apiClient.get(`/strongroom/vault-sessions/${sessionUuid}/`).then((response) => {
      const data = unwrapResponse(response);
      if (data.status !== "active" || !data.evidence) {
        throw new Error("Vault session is not active.");
      }
      return data;
    });
  },

  closeVaultSession(sessionUuid) {
    return apiClient.post(`/strongroom/vault-sessions/${sessionUuid}/close/`).then(unwrapResponse);
  },
};
