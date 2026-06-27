import apiClient from "./client";
import { unwrapResponse } from "./helpers";

export const votingApi = {
  getBallot(electionUuid) {
    return apiClient
      .get(`/voting/elections/${electionUuid}/ballot/`)
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
