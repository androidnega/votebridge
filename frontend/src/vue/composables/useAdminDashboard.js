import { computed } from "vue";
import { useDashboardStore } from "@/stores/dashboard";
import { adminKpiHealthStripe } from "@/config/adminWorkspace";

export function useAdminDashboard() {
  const dashboardStore = useDashboardStore();

  const overview = computed(() => dashboardStore.adminOverview || {});
  const primaryElection = computed(() => dashboardStore.openElectionsList[0] || null);
  const alertSummary = computed(() => overview.value.security_alerts || {});

  const electionHealthLevel = computed(() => {
    if (alertSummary.value.open > 0) return "critical";
    const status = primaryElection.value?.status || primaryElection.value?.election_status;
    if (status === "paused") return "attention";
    return "healthy";
  });

  const kpiCards = computed(() => {
    const election = primaryElection.value;
    const uuid = election?.uuid || election?.election_uuid;
    const status = election?.status || election?.election_status;

    return [
      {
        id: "active-elections",
        title: "Open elections",
        value: overview.value.active_elections ?? 0,
        hint: "Currently open or paused",
        healthStatus: (overview.value.active_elections ?? 0) > 0 ? "healthy" : "unknown",
        clickable: true,
        route: "/dashboard/elections",
      },
      {
        id: "turnout",
        title: "Live turnout",
        value: `${dashboardStore.turnoutPercentage}%`,
        detail: `${dashboardStore.totalVotesCast} of ${dashboardStore.registeredVoters} voters`,
        hint: "Updates while voting is open",
        healthStatus: dashboardStore.turnoutPercentage > 0 ? "healthy" : "unknown",
        clickable: Boolean(uuid && ["open", "paused"].includes(status)),
        route: uuid ? `/dashboard/elections/${uuid}/monitor` : null,
      },
      {
        id: "positions",
        title: "Positions configured",
        value: election?.position_count ?? "—",
        hint: election ? "In primary open election" : "No open election",
        healthStatus: (election?.position_count ?? 0) > 0 ? "healthy" : "attention",
        clickable: Boolean(uuid),
        route: uuid ? `/dashboard/elections/${uuid}/positions` : "/dashboard/elections",
      },
      {
        id: "candidates",
        title: "Approved candidates",
        value: election?.approved_candidate_count ?? "—",
        hint: election ? `${election?.candidate_count ?? 0} total nominated` : "Configure in workspace",
        healthStatus: (election?.approved_candidate_count ?? 0) > 0 ? "healthy" : "attention",
        clickable: Boolean(uuid),
        route: uuid ? `/dashboard/elections/${uuid}/candidates` : "/dashboard/elections",
      },
    ];
  });

  const quickActions = computed(() => {
    const election = primaryElection.value;
    const uuid = election?.uuid || election?.election_uuid;
    const status = election?.status || election?.election_status;
    const actions = [
      { id: "create", label: "Create election", route: "/dashboard/elections/create" },
      { id: "elections", label: "All elections", route: "/dashboard/elections" },
    ];
    if (uuid && ["open", "paused"].includes(status)) {
      actions.push({ id: "monitor", label: "Control room", route: `/dashboard/elections/${uuid}/monitor` });
    }
    if (uuid) {
      actions.push({ id: "readiness", label: "Readiness checklist", route: `/dashboard/elections/${uuid}/readiness` });
    }
    actions.push(
      { id: "results", label: "Results hub", route: "/dashboard/results" },
      { id: "reports", label: "Election reports", route: "/dashboard/reports" }
    );
    return actions;
  });

  const taskItems = computed(() => {
    const items = [];
    if (alertSummary.value.open) {
      items.push({
        id: "alerts",
        title: `${alertSummary.value.open} security alerts`,
        description: "Review in Reports or contact the super admin.",
      });
    }
    const election = primaryElection.value;
    if (election) {
      const status = election.status || election.election_status;
      if (status === "paused") {
        items.push({
          id: "paused",
          title: "Election is paused",
          description: "Resume voting when ready from the election workspace.",
        });
      }
      if (status === "draft" || status === "scheduled") {
        items.push({
          id: "readiness",
          title: "Complete readiness checks",
          description: "Validate positions, candidates, and eligibility before opening.",
        });
      }
    }
    return items;
  });

  const nextAction = computed(() => {
    const election = primaryElection.value;
    if (!election) return null;
    const uuid = election.uuid || election.election_uuid;
    const status = election.status || election.election_status;
    if (status === "open") {
      return { label: "Open control room", route: `/dashboard/elections/${uuid}/monitor` };
    }
    if (status === "paused") {
      return { label: "Review election", route: `/dashboard/elections/${uuid}` };
    }
    return { label: "Manage election", route: `/dashboard/elections/${uuid}` };
  });

  return {
    dashboardStore,
    overview,
    primaryElection,
    electionHealthLevel,
    kpiCards,
    quickActions,
    taskItems,
    nextAction,
    healthStripe: adminKpiHealthStripe,
  };
}
