/** Election workspace in-page navigation (admin). */

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

  return tabs;
}
