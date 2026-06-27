import apiClient from "./client";
import { unwrapResponse } from "./helpers";

export const dashboardApi = {
  getAdminOverview() {
    return apiClient.get("/dashboard/admin/").then(unwrapResponse);
  },

  getStudentOverview() {
    return apiClient.get("/dashboard/student/").then(unwrapResponse);
  },

  getSecurityFeed() {
    return apiClient.get("/dashboard/security-feed/").then(unwrapResponse);
  },

  getFraudFeed() {
    return apiClient.get("/dashboard/fraud-feed/").then(unwrapResponse);
  },
};

export { authApi } from "./auth";
export { electionsApi } from "./elections";
export { votingApi } from "./voting";
export { securityApi } from "./security";
export { fraudApi } from "./fraud";
export { usersApi } from "./users";
export { resultsApi } from "./results";
export { strongroomApi } from "./strongroom";
export { notificationsApi } from "./notifications";
export { ussdApi } from "./ussd";
export { operationsApi } from "./operations";
export { systemControlApi } from "./systemControl";
export { analyticsApi } from "./analytics";
