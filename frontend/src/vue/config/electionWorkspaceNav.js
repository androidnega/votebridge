/** Election workspace navigation — sidebar and module tabs. */

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

  if (["open", "paused"].includes(status)) {
    tabs.push({ label: "Control room", to: `${base}/monitor` });
  }

  if (["draft", "scheduled"].includes(status)) {
    tabs.push({ label: "Strong room committee", to: `${base}/committee` });
  }

  if (["closed", "archived"].includes(status)) {
    tabs.push({ label: "Vault access", to: `${base}/vault/access` });
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

  let tabs = [];
  if (isElectionOfficer) {
    tabs = getElectionWorkspaceNav(electionUuid, status);
  } else if (isStudent) {
    tabs = getElectionStudentNav(electionUuid, status);
  } else if (isSuperAdmin) {
    tabs = getElectionWorkspaceNav(electionUuid, status);
  }

  return tabs.map((tab) => ({
    name: tab.label,
    to: tab.to,
    exact: tab.exact,
    disabled: tab.disabled,
  }));
}
