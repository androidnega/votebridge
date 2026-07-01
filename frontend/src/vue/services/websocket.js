import { getAccessToken } from "@/api/helpers";

function isRealtimeEnabled() {
  return import.meta.env.VITE_ENABLE_REALTIME !== "false";
}

function getWebSocketOrigin() {
  const configured = import.meta.env.VITE_WS_BASE_URL;
  if (configured) {
    return String(configured).replace(/\/$/, "");
  }
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${protocol}//${window.location.host}`;
}

const REALTIME_PATHS = {
  dashboard: "/ws/realtime/dashboard/",
  security: "/ws/realtime/security/",
  fraud: "/ws/realtime/fraud/",
  results: "/ws/realtime/results/",
  strongroom: "/ws/realtime/strongroom/",
  election: (uuid) => `/ws/realtime/elections/${uuid}/`,
};

class RealtimeService {
  constructor() {
    this.sockets = new Map();
  }

  buildUrl(path) {
    const token = getAccessToken();
    if (!token) {
      throw new Error("Authentication required for realtime connection.");
    }
    const separator = path.includes("?") ? "&" : "?";
    return `${getWebSocketOrigin()}${path}${separator}token=${encodeURIComponent(token)}`;
  }

  connect(key, path, handlers = {}) {
    if (!isRealtimeEnabled()) {
      handlers.onStatusChange?.("disabled");
      return null;
    }

    this.disconnect(key);
    handlers.onStatusChange?.("connecting");

    let socket;
    try {
      socket = new WebSocket(this.buildUrl(path));
    } catch (error) {
      handlers.onStatusChange?.("disconnected");
      handlers.onError?.(error);
      return null;
    }

    let opened = false;

    socket.addEventListener("open", () => {
      opened = true;
      handlers.onOpen?.();
      handlers.onStatusChange?.("connected");
    });

    socket.addEventListener("message", (event) => {
      try {
        const message = JSON.parse(event.data);
        handlers.onMessage?.(message);
      } catch (error) {
        console.warn("Invalid realtime message", error);
      }
    });

    socket.addEventListener("close", () => {
      handlers.onStatusChange?.(opened ? "disconnected" : "unavailable");
      handlers.onClose?.();
    });

    socket.addEventListener("error", () => {
      if (!opened) {
        handlers.onStatusChange?.("unavailable");
      }
    });

    this.sockets.set(key, socket);
    return socket;
  }

  disconnect(key) {
    const existing = this.sockets.get(key);
    if (existing) {
      existing.close();
      this.sockets.delete(key);
    }
  }

  disconnectAll() {
    for (const key of [...this.sockets.keys()]) {
      this.disconnect(key);
    }
  }

  ping(key) {
    const socket = this.sockets.get(key);
    if (socket?.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ action: "ping" }));
    }
  }

  connectDashboard(handlers) {
    return this.connect("dashboard", REALTIME_PATHS.dashboard, handlers);
  }

  connectSecurity(handlers) {
    return this.connect("security", REALTIME_PATHS.security, handlers);
  }

  connectFraud(handlers) {
    return this.connect("fraud", REALTIME_PATHS.fraud, handlers);
  }

  connectResults(handlers) {
    return this.connect("results", REALTIME_PATHS.results, handlers);
  }

  connectStrongroom(handlers) {
    return this.connect("strongroom", REALTIME_PATHS.strongroom, handlers);
  }

  connectCommunications(handlers) {
    return this.connect("communications", "/ws/realtime/communications/", handlers);
  }

  connectNotifications(handlers) {
    return this.connect("notifications", "/ws/realtime/notifications/", handlers);
  }

  connectUssd(handlers) {
    return this.connect("ussd", "/ws/realtime/ussd/", handlers);
  }

  connectOperations(handlers) {
    return this.connect("operations", "/ws/realtime/operations/", handlers);
  }

  connectAnalytics(handlers) {
    return this.connect("analytics", "/ws/realtime/analytics/", handlers);
  }

  connectElection(uuid, handlers) {
    return this.connect(`election-${uuid}`, REALTIME_PATHS.election(uuid), handlers);
  }
}

export const realtimeService = new RealtimeService();
export default realtimeService;
