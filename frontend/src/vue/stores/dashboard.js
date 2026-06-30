import { defineStore } from "pinia";
import {
  dashboardApi,
  electionsApi,
  fraudApi,
  securityApi,
  usersApi,
} from "@/api";
import { extractApiError } from "@/api/helpers";
import realtimeService from "@/services/websocket";

const REALTIME_LABELS = {
  connected: "Live",
  connecting: "Connecting",
  disconnected: "Offline",
  unavailable: "Offline",
  disabled: "Offline",
  error: "Error",
};

const STUDENT_REFRESH_EVENTS = new Set([
  "ballot_submitted",
  "svt_issued",
  "svt_validated",
  "svt_consumed",
  "election_opened",
  "election_closed",
]);

const MAX_ACTIVITY_ITEMS = 25;
const MAX_LIVE_TURNOUT_POINTS = 30;

function currentHourLabel(date = new Date()) {
  return `${String(date.getHours()).padStart(2, "0")}:00`;
}

function currentTimeLabel(date = new Date()) {
  return date.toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" });
}

function cloneTrendBuckets(buckets = []) {
  return buckets.map((point) => ({ ...point }));
}

function mergeAdminOverview(current, incoming) {
  if (!current) return incoming;
  const merged = { ...current, ...incoming };
  if (incoming.security_alerts && current.security_alerts) {
    merged.security_alerts = { ...current.security_alerts, ...incoming.security_alerts };
  }
  if (incoming.fraud_cases && current.fraud_cases) {
    merged.fraud_cases = { ...current.fraud_cases, ...incoming.fraud_cases };
  }
  if (incoming.monitoring && current.monitoring) {
    merged.monitoring = { ...current.monitoring, ...incoming.monitoring };
    if (incoming.monitoring.system_health || current.monitoring.system_health) {
      merged.monitoring.system_health = {
        ...current.monitoring.system_health,
        ...incoming.monitoring.system_health,
      };
    }
  }
  return merged;
}

function mergeStudentOverview(current, incoming) {
  if (!current) return incoming;
  return { ...current, ...incoming };
}

export const useDashboardStore = defineStore("dashboard", {
  state: () => ({
    studentOverview: null,
    adminOverview: null,
    scheduledElections: [],
    openElectionsList: [],
    totalElectionsCount: 0,
    monitoringSummary: null,
    fraudIntegrity: null,
    securityFeed: null,
    activeUsersCount: 0,
    verificationResult: null,
    activityFeed: [],
    adminTrends: {
      votesHourly: [],
      turnoutHourly: [],
      turnoutLive: [],
    },
    realtimeStatus: "disconnected",
    realtimeScope: null,
    loading: false,
    verifying: false,
    error: null,
  }),

  getters: {
    realtimeLabel: (state) => REALTIME_LABELS[state.realtimeStatus] || "Live",
    isRealtimeLive: (state) => state.realtimeStatus === "connected",
    studentActiveElections: (state) => state.studentOverview?.active_elections || [],
    studentVotingHistory: (state) =>
      (state.studentOverview?.active_elections || []).filter(
        (row) => row.ballot_submitted || row.confirmation_status === "recorded"
      ),
    pendingSecurityAlerts: (state) => state.adminOverview?.security_alerts?.open ?? 0,
    openFraudCases: (state) => state.adminOverview?.fraud_cases?.open_cases ?? 0,
    turnoutPercentage: (state) => state.adminOverview?.turnout_percentage ?? 0,
    totalVotesCast: (state) => state.adminOverview?.total_votes_cast ?? 0,
    registeredVoters: (state) => state.adminOverview?.registered_voters ?? 0,
  },

  actions: {
    async fetchStudentDashboard() {
      this.loading = true;
      this.error = null;
      try {
        const [overview, scheduled] = await Promise.all([
          dashboardApi.getStudentOverview(),
          electionsApi.list({ status: "scheduled", page_size: 10 }),
        ]);
        this.studentOverview = overview;
        this.scheduledElections = scheduled.items;
        return overview;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchAdminDashboard() {
      this.loading = true;
      this.error = null;
      try {
        const [overview, allElections, openElections, pausedElections, scheduledElections] =
          await Promise.all([
          dashboardApi.getAdminOverview(),
          electionsApi.list({ page_size: 1 }),
          electionsApi.list({ status: "open", page_size: 10 }),
          electionsApi.list({ status: "paused", page_size: 10 }),
          electionsApi.list({ status: "scheduled", page_size: 10 }),
        ]);
        this.adminOverview = overview;
        this.totalElectionsCount = allElections.count;
        this.openElectionsList = [...openElections.items, ...pausedElections.items];
        this.scheduledElections = scheduledElections.items;
        this.seedAdminTrends(overview);
        return overview;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchSuperAdminDashboard() {
      this.loading = true;
      this.error = null;
      try {
        const [overview, monitoring, fraudReport, elections, users, securityFeed] =
          await Promise.all([
            dashboardApi.getAdminOverview(),
            securityApi.getMonitoringSummary(),
            fraudApi.getIntegrityReport(),
            electionsApi.list({ page_size: 10 }),
            usersApi.list({ is_active: true, page_size: 1 }),
            dashboardApi.getSecurityFeed().catch(() => null),
          ]);

        this.adminOverview = overview;
        this.seedAdminTrends(overview);
        this.monitoringSummary = monitoring;
        this.fraudIntegrity = fraudReport;
        this.totalElectionsCount = elections.count;
        this.openElectionsList = elections.items.filter((e) => e.status === "open");
        this.activeUsersCount = users.count;
        this.securityFeed = securityFeed;
        return { overview, monitoring, fraudReport };
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async refreshStudentDashboard() {
      try {
        this.studentOverview = await dashboardApi.getStudentOverview();
      } catch {
        /* keep existing snapshot */
      }
    },

    connectRealtime(scope = "admin") {
      this.realtimeScope = scope;
      this.realtimeStatus = "connecting";

      realtimeService.connectDashboard({
        onStatusChange: (status) => {
          this.realtimeStatus = status;
        },
        onMessage: (message) => {
          this.handleRealtimeMessage(message, scope);
        },
      });
    },

    disconnectRealtime() {
      realtimeService.disconnect("dashboard");
      this.realtimeStatus = "disconnected";
      this.realtimeScope = null;
    },

    handleRealtimeMessage(message, scope) {
      const { event, data, timestamp } = message;
      if (!event || !data) return;

      if (event === "dashboard_stats") {
        if (data.role === "admin" && (scope === "admin" || scope === "super-admin")) {
          this.adminOverview = mergeAdminOverview(this.adminOverview, data);
          if (data.trends) {
            this.seedAdminTrends(this.adminOverview);
          } else if (data.turnout_percentage !== undefined) {
            this.recordLiveTurnout(data.turnout_percentage);
          }
          if (data.fraud_cases) {
            this.fraudIntegrity = { ...this.fraudIntegrity, ...data.fraud_cases };
          }
        }
        if (data.role === "student" && scope === "student") {
          this.studentOverview = mergeStudentOverview(this.studentOverview, data);
        }
        return;
      }

      if (scope === "admin" || scope === "super-admin") {
        this.handleAdminRealtimeEvent(event, data, timestamp);
      }

      if (scope === "student" && STUDENT_REFRESH_EVENTS.has(event)) {
        this.refreshStudentDashboard();
      }
    },

    handleAdminRealtimeEvent(event, data, timestamp) {
      const overview = this.adminOverview || {};

      if (event === "ballot_submitted") {
        if (data.total_votes_cast !== undefined) {
          overview.total_votes_cast = data.total_votes_cast;
        }
        if (data.turnout_percentage !== undefined) {
          overview.turnout_percentage = data.turnout_percentage;
        }
        if (data.monitoring) {
          overview.monitoring = { ...(overview.monitoring || {}), ...data.monitoring };
        } else if (overview.monitoring) {
          overview.monitoring = {
            ...overview.monitoring,
            voters_participated: data.voters_participated ?? overview.monitoring.voters_participated,
            turnout_percentage: data.turnout_percentage ?? overview.monitoring.turnout_percentage,
            total_votes_cast: data.total_votes_cast ?? overview.monitoring.total_votes_cast,
          };
        }
        this.adminOverview = { ...overview };
        const turnout =
          data.election_turnout_percentage ??
          data.turnout_percentage ??
          overview.turnout_percentage;
        this.recordLiveTurnout(turnout);
        this.incrementVotesHourly(data.votes_count ?? 1);
        this.updateTurnoutHourly(turnout);
        this.prependActivity({
          id: `ballot-${timestamp || Date.now()}`,
          title: `Ballot submitted — ${data.election_title || "Election"}`,
          description: `${data.votes_count ?? 0} vote(s) recorded. Aggregate totals updated.`,
          created_at: timestamp || new Date().toISOString(),
          event_type: event,
        });
        return;
      }

      if (event === "security_alert_created") {
        const alerts = { ...(overview.security_alerts || {}) };
        alerts.open = (alerts.open || 0) + 1;
        overview.security_alerts = alerts;
        this.adminOverview = { ...overview };
        this.prependActivity({
          id: data.alert_id || `alert-${Date.now()}`,
          title: data.title || "Security alert",
          description: data.description || "New security alert detected.",
          created_at: data.created_at || timestamp,
          event_type: event,
        });
        return;
      }

      if (event === "security_alert_resolved") {
        const alerts = { ...(overview.security_alerts || {}) };
        alerts.open = Math.max(0, (alerts.open || 0) - 1);
        alerts.resolved = (alerts.resolved || 0) + 1;
        overview.security_alerts = alerts;
        this.adminOverview = { ...overview };
        this.prependActivity({
          id: `resolved-${data.alert_id || Date.now()}`,
          title: `Alert resolved — ${data.title || "Security alert"}`,
          description: "Security alert marked resolved.",
          created_at: data.resolved_at || timestamp,
          event_type: event,
        });
        return;
      }

      if (event === "fraud_case_created") {
        const fraud = { ...(overview.fraud_cases || {}) };
        fraud.total_fraud_cases = (fraud.total_fraud_cases || 0) + 1;
        fraud.open_cases = (fraud.open_cases || 0) + 1;
        overview.fraud_cases = fraud;
        this.adminOverview = { ...overview };
        this.fraudIntegrity = { ...this.fraudIntegrity, open_cases: fraud.open_cases };
        this.prependActivity({
          id: data.fraud_case_id || `fraud-${Date.now()}`,
          title: data.alert_title || "Fraud case opened",
          description: `Severity: ${data.severity || "unknown"}. Risk score: ${data.risk_score ?? "—"}.`,
          created_at: data.created_at || timestamp,
          event_type: event,
        });
        return;
      }

      if (event === "fraud_case_resolved") {
        const fraud = { ...(overview.fraud_cases || {}) };
        fraud.open_cases = Math.max(0, (fraud.open_cases || 0) - 1);
        fraud.resolved_cases = (fraud.resolved_cases || 0) + 1;
        overview.fraud_cases = fraud;
        this.adminOverview = { ...overview };
        this.fraudIntegrity = {
          ...this.fraudIntegrity,
          open_cases: fraud.open_cases,
          resolved_cases: fraud.resolved_cases,
        };
        this.prependActivity({
          id: `fraud-resolved-${data.fraud_case_id || Date.now()}`,
          title: `Fraud case resolved — ${data.alert_title || "Case"}`,
          description: "Investigation closed.",
          created_at: data.updated_at || timestamp,
          event_type: event,
        });
        return;
      }

      if (event === "fraud_case_escalated") {
        this.prependActivity({
          id: `fraud-escalated-${data.fraud_case_id || Date.now()}`,
          title: `Fraud case escalated — ${data.alert_title || "Case"}`,
          description: "Escalated for senior review.",
          created_at: data.updated_at || timestamp,
          event_type: event,
        });
        return;
      }

      if (event === "election_opened") {
        overview.active_elections = (overview.active_elections || 0) + 1;
        this.adminOverview = { ...overview };
        this.prependActivity({
          id: `open-${data.election_uuid || Date.now()}`,
          title: `Election opened — ${data.election_title || "Election"}`,
          description: "Voting is now live.",
          created_at: timestamp || new Date().toISOString(),
          event_type: event,
        });
        return;
      }

      if (event === "election_closed") {
        overview.active_elections = Math.max(0, (overview.active_elections || 0) - 1);
        this.adminOverview = { ...overview };
        this.prependActivity({
          id: `close-${data.election_uuid || Date.now()}`,
          title: `Election closed — ${data.election_title || "Election"}`,
          description: "Voting has ended.",
          created_at: timestamp || new Date().toISOString(),
          event_type: event,
        });
      }
    },

    prependActivity(item) {
      this.activityFeed = [item, ...this.activityFeed].slice(0, MAX_ACTIVITY_ITEMS);
    },

    seedAdminTrends(overview) {
      if (!overview) return;
      const trends = overview.trends || {};
      const turnout = overview.turnout_percentage ?? 0;
      this.adminTrends = {
        votesHourly: cloneTrendBuckets(trends.votes_hourly),
        turnoutHourly: cloneTrendBuckets(trends.turnout_hourly),
        turnoutLive: [{ label: currentTimeLabel(), value: turnout }],
      };
    },

    recordLiveTurnout(turnout) {
      if (turnout === undefined || turnout === null) return;
      const nextPoint = { label: currentTimeLabel(), value: Number(turnout) };
      const points = [...this.adminTrends.turnoutLive, nextPoint].slice(-MAX_LIVE_TURNOUT_POINTS);
      this.adminTrends = { ...this.adminTrends, turnoutLive: points };
    },

    incrementVotesHourly(voteCount = 1) {
      const label = currentHourLabel();
      const buckets = cloneTrendBuckets(this.adminTrends.votesHourly);
      const index = buckets.findIndex((point) => point.label === label);
      if (index >= 0) {
        buckets[index] = { ...buckets[index], value: buckets[index].value + voteCount };
      } else {
        buckets.push({ label, value: voteCount });
      }
      this.adminTrends = { ...this.adminTrends, votesHourly: buckets };
    },

    updateTurnoutHourly(turnout) {
      if (turnout === undefined || turnout === null) return;
      const label = currentHourLabel();
      const buckets = cloneTrendBuckets(this.adminTrends.turnoutHourly);
      const index = buckets.findIndex((point) => point.label === label);
      if (index >= 0) {
        buckets[index] = { ...buckets[index], value: Number(turnout) };
      } else {
        buckets.push({ label, value: Number(turnout) });
      }
      this.adminTrends = { ...this.adminTrends, turnoutHourly: buckets };
    },

    async verifyBallotToken(tokenCode) {
      this.verifying = true;
      this.error = null;
      try {
        this.verificationResult = await securityApi.verifySvt(tokenCode.trim());
        return this.verificationResult;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.verifying = false;
      }
    },

    clearVerification() {
      this.verificationResult = null;
    },
  },
});
