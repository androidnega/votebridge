/** Election workspace in-page navigation (admin). */

export function getElectionWorkspaceNav(electionUuid, status) {
  const base = `/elections/${electionUuid}`;
  const tabs = [
    { label: "Overview", to: base, exact: true },
    { label: "Positions", to: `${base}/positions` },
    { label: "Candidates", to: `${base}/candidates` },
    { label: "Eligibility", to: `${base}/eligibility` },
    { label: "Readiness", to: `${base}/readiness` },
  ];

  if (["open", "paused"].includes(status)) {
    tabs.push({ label: "Monitor", to: `${base}/monitor` });
  }

  return tabs;
}

export const electionWorkspaceNav = [];
