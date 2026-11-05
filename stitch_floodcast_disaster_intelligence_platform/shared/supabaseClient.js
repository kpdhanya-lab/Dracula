/**
 * 🌊 BasinShift: FloodCast Supabase Integration Client
 * Connects the frontend to Supabase Realtime & REST API.
 */

const SUPABASE_PROJECT_URL = window.SUPABASE_URL || "https://kgdyupauslkdqojqcwkw.supabase.co";
// Configurable via window.SUPABASE_API_KEY, server config (/api/config), or environment
const SUPABASE_API_KEY = window.SUPABASE_API_KEY || "";

class BasinShiftDB {
  constructor() {
    this.url = SUPABASE_PROJECT_URL;
    this.key = SUPABASE_API_KEY;
    this.client = null;
    this.initClient();
    this.fetchServerConfig();
  }

  async fetchServerConfig() {
    if (!this.key) {
      try {
        const res = await fetch("/api/config");
        if (res.ok) {
          const cfg = await res.json();
          if (cfg.supabaseKey) {
            this.url = cfg.supabaseUrl || this.url;
            this.key = cfg.supabaseKey;
            this.initClient();
          }
        }
      } catch (_) {
        // Fallback for offline/standalone execution
      }
    }
  }

  initClient() {
    if (this.key && window.supabase && typeof window.supabase.createClient === "function") {
      this.client = window.supabase.createClient(this.url, this.key, {
        realtime: {
          params: {
            eventsPerSecond: 10
          }
        }
      });
      console.log("⚡ BasinShift Supabase Client initialized successfully.");
    } else {
      console.warn("Supabase SDK waiting or no API key set.");
    }
  }

  async _fetch(endpoint, options = {}) {
    const url = `${this.url}/rest/v1/${endpoint}`;
    const headers = {
      "apikey": this.key,
      "Authorization": `Bearer ${this.key}`,
      "Content-Type": "application/json",
      ...(options.headers || {})
    };
    try {
      const res = await fetch(url, { ...options, headers });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${await res.text()}`);
      }
      return await res.json();
    } catch (err) {
      console.error(`BasinShiftDB Error [${endpoint}]:`, err);
      throw err;
    }
  }

  // 1. Fetch catchments
  async getCatchments() {
    return await this._fetch("catchments?select=*&order=name.asc");
  }

  // 2. Fetch latest active alerts
  async getActiveAlerts() {
    return await this._fetch("flood_alerts?select=*,catchments(name,safe_discharge_threshold)&is_acknowledged=eq.false&order=created_at.desc");
  }

  // 3. Acknowledge an alert
  async acknowledgeAlert(alertId, acknowledgedBy = "Operator-1") {
    const url = `${this.url}/rest/v1/flood_alerts?id=eq.${alertId}`;
    const headers = {
      "apikey": this.key,
      "Authorization": `Bearer ${this.key}`,
      "Content-Type": "application/json",
      "Prefer": "return=representation"
    };
    const res = await fetch(url, {
      method: "PATCH",
      headers,
      body: JSON.stringify({
        is_acknowledged: true,
        acknowledged_by: acknowledgedBy,
        acknowledged_at: new Date().toISOString()
      })
    });
    return await res.json();
  }

  // 4. Fetch latest model forecast for a catchment
  async getLatestForecast(catchmentId = "camels_05503800") {
    const records = await this._fetch(`model_forecasts?catchment_id=eq.${catchmentId}&order=forecast_origin.desc&limit=1`);
    return records && records.length > 0 ? records[0] : null;
  }

  // 5. Fetch historical telemetry window
  async getHistoricalTelemetry(catchmentId = "camels_05503800", days = 30) {
    return await this._fetch(`historical_telemetry?catchment_id=eq.${catchmentId}&order=recorded_date.desc&limit=${days}`);
  }

  // 6. Fetch production model evaluation metrics (for Model Lab)
  async getModelMetrics() {
    const records = await this._fetch("model_experiments?order=created_at.desc&limit=1");
    return records && records.length > 0 ? records[0] : null;
  }

  // 7. Copilot conversation history
  async getCopilotMessages(sessionId = "default-session", limit = 20) {
    return await this._fetch(`copilot_messages?session_id=eq.${sessionId}&order=created_at.asc&limit=${limit}`);
  }

  // 8. Save Copilot prompt and response
  async logCopilotMessage(sessionId, catchmentId, userPrompt, assistantResponse, telemetryContext = {}) {
    const url = `${this.url}/rest/v1/copilot_messages`;
    const headers = {
      "apikey": this.key,
      "Authorization": `Bearer ${this.key}`,
      "Content-Type": "application/json",
      "Prefer": "return=representation"
    };
    const res = await fetch(url, {
      method: "POST",
      headers,
      body: JSON.stringify({
        session_id: sessionId || "default-session",
        catchment_id: catchmentId,
        user_prompt: userPrompt,
        assistant_response: assistantResponse,
        telemetry_grounding: telemetryContext
      })
    });
    return await res.json();
  }

  // 9. Subscribe to Realtime Alerts
  onRealtimeAlerts(callback) {
    if (this.client) {
      const channel = this.client
        .channel("public:flood_alerts")
        .on(
          "postgres_changes",
          { event: "*", schema: "public", table: "flood_alerts" },
          (payload) => {
            console.log("🚨 Realtime alert event received:", payload);
            if (typeof callback === "function") {
              callback(payload);
            }
          }
        )
        .subscribe((status) => {
          console.log("Realtime alert subscription status:", status);
        });
      return channel;
    }
  }
}

// Attach globally
window.BasinShiftDB = new BasinShiftDB();

