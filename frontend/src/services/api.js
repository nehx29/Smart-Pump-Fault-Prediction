/**
 * API Service — Smart Pump Fault Prediction System
 *
 * Uses relative /api path by default (leverages Vite dev proxy).
 * Override with VITE_API_URL environment variable for production or tunnel deployments.
 */
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

/* ------------------------------------------------------------------ */
/*  Core API Functions                                                 */
/* ------------------------------------------------------------------ */

export async function getHealth() {
  try {
    const res = await fetch(`${API_BASE_URL}/health`, { signal: AbortSignal.timeout(5000) });
    if (!res.ok) return { status: 'error', model_loaded: false };
    return await res.json();
  } catch {
    return { status: 'error', model_loaded: false };
  }
}

export async function getLatest() {
  try {
    const res = await fetch(`${API_BASE_URL}/latest`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    return { success: false, data: null, error: err.message };
  }
}

export async function getHistory(limit = 20) {
  try {
    const res = await fetch(`${API_BASE_URL}/history?limit=${limit}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    return { success: false, data: [], count: 0, error: err.message };
  }
}

export async function predictPumpFault(data) {
  try {
    const res = await fetch(`${API_BASE_URL}/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    let json;
    try {
      json = await res.json();
    } catch {
      return { success: false, error: `Invalid response from prediction service (HTTP ${res.status})` };
    }
    if (json && typeof json.prediction === 'string' && !('success' in json)) {
      json.success = true;
    }
    if (!res.ok) {
      return {
        success: false,
        error: json.error || `Prediction request failed (HTTP ${res.status})`,
      };
    }
    return json;
  } catch (err) {
    return { success: false, error: err.message };
  }
}

export async function sendSensorData(data) {
  try {
    const res = await fetch(`${API_BASE_URL}/sensor-data`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    let json;
    try {
      json = await res.json();
    } catch {
      return { success: false, error: `Invalid response while storing reading (HTTP ${res.status})` };
    }
    if (!res.ok && json.success !== false) {
      json.success = false;
      json.error = json.error || `Failed to store reading (HTTP ${res.status})`;
    }
    return json;
  } catch (err) {
    return { success: false, error: err.message };
  }
}

export async function getModelInfo() {
  try {
    const res = await fetch(`${API_BASE_URL}/model-info`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    return { success: false, data: null, error: err.message };
  }
}

export async function getAlerts(limit = 50, faultsOnly = true) {
  try {
    const res = await fetch(`${API_BASE_URL}/alerts?limit=${limit}&faults_only=${faultsOnly}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    return { success: false, data: [], count: 0, error: err.message };
  }
}

/* ------------------------------------------------------------------ */
/*  Backward-compatible aliases                                        */
/* ------------------------------------------------------------------ */
export const fetchHealthStatus = getHealth;
export const fetchLatestReading = getLatest;
export const fetchSensorHistory = getHistory;
export const postSensorReading = sendSensorData;
export const postStandalonePrediction = predictPumpFault;
export const fetchModelInfo = getModelInfo;
export const fetchAlerts = getAlerts;
