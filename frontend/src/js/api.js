/**
 * VoteBridge API client and auth token storage.
 */
const VoteBridgeAPI = {
  baseUrl: "/api/v1",

  getAccessToken() {
    return localStorage.getItem("vb_access_token");
  },

  getRefreshToken() {
    return localStorage.getItem("vb_refresh_token");
  },

  setTokens(access, refresh) {
    if (access) localStorage.setItem("vb_access_token", access);
    if (refresh) localStorage.setItem("vb_refresh_token", refresh);
  },

  clearTokens() {
    localStorage.removeItem("vb_access_token");
    localStorage.removeItem("vb_refresh_token");
  },

  getDeviceFingerprint() {
    let fp = localStorage.getItem("vb_device_fingerprint");
    if (!fp) {
      const parts = [
        navigator.userAgent,
        navigator.language,
        screen.width,
        screen.height,
        screen.colorDepth,
        Intl.DateTimeFormat().resolvedOptions().timeZone,
      ];
      fp = parts.join("|");
      localStorage.setItem("vb_device_fingerprint", fp);
    }
    return fp;
  },

  async request(path, options = {}) {
    const headers = options.headers || {};
    const token = this.getAccessToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    headers["X-Device-Fingerprint"] = this.getDeviceFingerprint();
    if (!headers["Content-Type"] && !(options.body instanceof FormData)) {
      headers["Content-Type"] = "application/json";
    }

    const response = await fetch(`${this.baseUrl}${path}`, {
      ...options,
      headers,
    });

    if (response.status === 401 && this.getRefreshToken()) {
      const refreshed = await this.refreshToken();
      if (refreshed) {
        headers["Authorization"] = `Bearer ${this.getAccessToken()}`;
        return fetch(`${this.baseUrl}${path}`, { ...options, headers });
      }
    }

    return response;
  },

  async refreshToken() {
    const refresh = this.getRefreshToken();
    if (!refresh) return false;

    const response = await fetch(`${this.baseUrl}/accounts/auth/token/refresh/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh }),
    });

    if (!response.ok) {
      this.clearTokens();
      return false;
    }

    const data = await response.json();
    this.setTokens(data.data?.access, data.data?.refresh);
    return true;
  },

  async getJson(path) {
    const response = await this.request(path);
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error?.message || "Request failed");
    }
    return data;
  },

  async postJson(path, body) {
    const response = await this.request(path, {
      method: "POST",
      body: JSON.stringify(body),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error?.message || "Request failed");
    }
    return data;
  },

  async patchJson(path, body) {
    const response = await this.request(path, {
      method: "PATCH",
      body: JSON.stringify(body),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error?.message || "Request failed");
    }
    return data;
  },

  async delete(path) {
    const response = await this.request(path, { method: "DELETE" });
    if (!response.ok && response.status !== 204) {
      const data = await response.json();
      throw new Error(data.error?.message || "Delete failed");
    }
    return true;
  },

  async postForm(path, formData) {
    const response = await this.request(path, {
      method: "POST",
      body: formData,
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error?.message || "Request failed");
    }
    return data;
  },

  async patchForm(path, formData) {
    const response = await this.request(path, {
      method: "PATCH",
      body: formData,
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error?.message || "Request failed");
    }
    return data;
  },
};

window.VoteBridgeAPI = VoteBridgeAPI;
