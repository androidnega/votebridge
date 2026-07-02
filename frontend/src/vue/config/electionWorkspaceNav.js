/** Election workspace navigation — presentation-focused election management tabs. */

import { dashboardPath } from "@/config/routes";

export function getElectionWorkspaceNav(electionUuid, status) {
  const base = dashboardPath(`elections/${electionUuid}`);
  const tabs = [
    { label: "Overview", to: base, exact: true },
    { label: "Positions", to: `${base}/positions` },
    { label: "Candidates", to: `${base}/candidates` },
    { label: "Eligibility", to: `${base}/eligibility` },
    { label: "Readiness", to: `${base}/readiness` },
  ];

  if (["open", "paused", "closed"].includes(status)) {
    tabs.push({ label: "Monitor", to: `${base}/monitor` });
  }

  if (["closed", "archived"].includes(status)) {
    tabs.push({ label: "Analytics", to: `${base}/analytics` });
  }

  return tabs;
}

export function getElectionStudentNav(electionUuid, status) {
  const base = dashboardPath(`elections/${electionUuid}`);
  const canVote = ["open", "paused"].includes(status);

  return [
    { label: "Overview", to: base, exact: true },
    { label: "Vote", to: `${base}/vote`, disabled: !canVote },
    { label: "Confirmation", to: `${base}/confirmation` },
  ];
}

/** Sidebar child links while viewing a specific election. */
export function getElectionSidebarChildren(electionUuid, status, { isElectionOfficer, isStudent, isSuperAdmin } = {}) {
  if (!electionUuid) return [];

  if (isElectionOfficer) {
    return getElectionWorkspaceNav(electionUuid, status).map((tab) => ({
      name: tab.label,
      to: tab.to,
      exact: tab.exact,
      disabled: tab.disabled,
    }));
  }

  if (isStudent) {
    return getElectionStudentNav(electionUuid, status).map((tab) => ({
      name: tab.label,
      to: tab.to,
      exact: tab.exact,
      disabled: tab.disabled,
    }));
  }

  if (isSuperAdmin) {
    return getElectionWorkspaceNav(electionUuid, status)
      .filter((tab) => ["Overview", "Monitor", "Analytics"].includes(tab.label))
      .map((tab) => ({
        name: tab.label,
        to: tab.to,
        exact: tab.exact,
        disabled: tab.disabled,
      }));
  }

  return [];
}
