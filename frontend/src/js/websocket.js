/**
 * VoteBridge WebSocket client for Django Channels realtime feeds.
 */
const VoteBridgeRealtime = {
  sockets: {},

  buildUrl(path) {
    const token = VoteBridgeAPI.getAccessToken();
    if (!token) {
      throw new Error("Authentication required for realtime connection.");
    }
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const separator = path.includes("?") ? "&" : "?";
    return `${protocol}//${window.location.host}${path}${separator}token=${encodeURIComponent(token)}`;
  },

  connect(key, path, handlers = {}) {
    this.disconnect(key);

    let ws;
    try {
      ws = new WebSocket(this.buildUrl(path));
    } catch (error) {
      handlers.onError?.(error);
      return null;
    }

    ws.onopen = () => {
      handlers.onOpen?.();
      handlers.onStatusChange?.("connected");
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        handlers.onMessage?.(message);
      } catch (error) {
        console.warn("Invalid realtime message", error);
      }
    };

    ws.onclose = () => {
      handlers.onStatusChange?.("disconnected");
      handlers.onClose?.();
    };

    ws.onerror = () => {
      handlers.onStatusChange?.("error");
      handlers.onError?.(new Error("WebSocket connection error"));
    };

    this.sockets[key] = ws;
    return ws;
  },

  disconnect(key) {
    const existing = this.sockets[key];
    if (existing) {
      existing.close();
      delete this.sockets[key];
    }
  },

  disconnectAll() {
    Object.keys(this.sockets).forEach((key) => this.disconnect(key));
  },

  ping(key) {
    const ws = this.sockets[key];
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ action: "ping" }));
    }
  },
};

window.VoteBridgeRealtime = VoteBridgeRealtime;
