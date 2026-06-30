import { computed } from "vue";
import { storeToRefs } from "pinia";
import { useDashboardStore } from "@/stores/dashboard";

const HEALTH_VARIANTS = {
  healthy: { stripe: "bg-success-600", text: "text-success-700", bg: "bg-success-600/10" },
  warning: { stripe: "bg-warning-600", text: "text-warning-700", bg: "bg-warning-600/10" },
  critical: { stripe: "bg-danger-600", text: "text-danger-700", bg: "bg-danger-600/10" },
  unknown: { stripe: "bg-slate-400", text: "text-slate-600", bg: "bg-surface-muted" },
};

function healthVariant(status) {
  return HEALTH_VARIANTS[status] || HEALTH_VARIANTS.unknown;
}

export function useAdminMonitoring() {
  const dashboardStore = useDashboardStore();
  const { adminOverview, isRealtimeLive } = storeToRefs(dashboardStore);

  const monitoring = computed(() => adminOverview.value?.monitoring || {});

  const primaryElectionTitle = computed(
    () => adminOverview.value?.primary_election?.title || null
  );

  const metrics = computed(() => {
    const data = monitoring.value;
    const health = data.system_health || {};
    const healthStyle = healthVariant(health.status);

    return [
      {
        id: "total-turnout",
        label: "Total turnout",
        value: data.voters_participated ?? 0,
        detail: data.eligible_voters
          ? `${data.voters_participated ?? 0} of ${data.eligible_voters} voters have voted`
          : "",
        healthStatus: (data.voters_participated ?? 0) > 0 ? "healthy" : "unknown",
      },
      {
        id: "turnout-percentage",
        label: "Turnout percentage",
        value: `${data.turnout_percentage ?? dashboardStore.turnoutPercentage ?? 0}%`,
        detail: "Eligible voter participation rate",
        healthStatus: (data.turnout_percentage ?? 0) > 0 ? "healthy" : "unknown",
      },
      {
        id: "web-votes",
        label: "Web votes",
        value: data.web_votes ?? 0,
        detail: data.web_ballots ? `${data.web_ballots} ballot selections` : "Distinct web voters",
        healthStatus: data.voting_channels?.web_enabled ? "healthy" : "attention",
      },
      {
        id: "ussd-votes",
        label: "USSD votes",
        value: data.ussd_votes ?? 0,
        detail: data.ussd_ballots ? `${data.ussd_ballots} ballot selections` : "Distinct USSD voters",
        healthStatus: data.voting_channels?.ussd_enabled ? "healthy" : "attention",
      },
      {
        id: "active-sessions",
        label: "Active USSD sessions",
        value: data.active_sessions ?? 0,
        detail: "Live menu sessions",
        healthStatus: "unknown",
      },
      {
        id: "failed-sessions",
        label: "Failed USSD sessions",
        value: data.failed_sessions ?? 0,
        detail: "Requires follow-up if elevated",
        healthStatus: (data.failed_sessions ?? 0) > 0 ? "attention" : "healthy",
      },
      {
        id: "fraud-alerts",
        label: "Fraud alerts",
        value: data.fraud_alerts ?? dashboardStore.openFraudCases ?? 0,
        detail: "Open fraud cases",
        healthStatus: (data.fraud_alerts ?? 0) > 0 ? "critical" : "healthy",
      },
      {
        id: "security-alerts",
        label: "Security alerts",
        value: data.security_alerts ?? dashboardStore.pendingSecurityAlerts ?? 0,
        detail: "Unresolved incidents",
        healthStatus: (data.security_alerts ?? 0) > 0 ? "attention" : "healthy",
      },
      {
        id: "system-health",
        label: "System health",
        value: health.label || "Unavailable",
        detail: health.status ? health.status.replace(/_/g, " ") : "",
        healthStatus: health.status === "healthy" ? "healthy" : health.status === "critical" ? "critical" : health.status === "warning" ? "attention" : "unknown",
        healthStyle,
      },
    ];
  });

  return {
    metrics,
    primaryElectionTitle,
    isLive: isRealtimeLive,
    hasMonitoring: computed(() => Boolean(adminOverview.value?.monitoring)),
  };
}
