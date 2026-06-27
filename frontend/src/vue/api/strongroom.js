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

  verifyIntegrity(electionUuid) {
    return apiClient.post(`/strongroom/elections/${electionUuid}/verify/`).then(unwrapResponse);
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
};
