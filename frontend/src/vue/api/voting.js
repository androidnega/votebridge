import apiClient from "./client";
import { unwrapResponse } from "./helpers";

export const votingApi = {
  getBallot(electionUuid) {
    return apiClient
      .get(`/voting/elections/${electionUuid}/ballot/`)
      .then(unwrapResponse);
  },

  getPresenceStatus(electionUuid) {
    return apiClient
      .get(`/voting/elections/${electionUuid}/presence/status/`)
      .then(unwrapResponse);
  },

  submitPresenceCapture(electionUuid, formData) {
    // Let axios set multipart boundary automatically — do not set Content-Type manually.
    return apiClient
      .post(`/voting/elections/${electionUuid}/presence/`, formData)
      .then(unwrapResponse);
  },

  submitBallot(electionUuid, payload) {
    return apiClient
      .post(`/voting/elections/${electionUuid}/submit/`, payload)
      .then(unwrapResponse);
  },

  listMyVotes(electionUuid) {
    return apiClient
      .get(`/voting/elections/${electionUuid}/my-votes/`)
      .then(unwrapResponse);
  },
};
