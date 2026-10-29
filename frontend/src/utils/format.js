export function formatConfidence(confidence) {
  if (confidence == null || confidence === '') return 'Unavailable';
  const value = Number(confidence);
  if (!Number.isFinite(value)) return 'Unavailable';
  const pct = value * 100;
  // Show full precision so users can see that 0.999997 ≠ 1.000000
  if (pct >= 99.95) return `${pct.toFixed(2)}%`;
  if (pct >= 10) return `${pct.toFixed(1)}%`;
  return `${pct.toFixed(2)}%`;
}

export function formatTimestamp(timestamp) {
  if (!timestamp) return 'Unknown';
  const raw = String(timestamp);
  const iso = raw.endsWith('Z') || raw.includes('+') ? raw : `${raw.replace(' ', 'T')}Z`;
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return raw;
  return date.toLocaleString();
}

export function formatNumber(value, digits = 2) {
  if (value == null || value === '') return '—';
  const n = Number(value);
  if (!Number.isFinite(n)) return '—';
  return n.toFixed(digits);
}

export function sourceLabel(source) {
  const value = (source || 'UNKNOWN').toUpperCase();
  if (value === 'WOKWI_SIMULATED' || value === 'WOKWI') return 'Wokwi simulator';
  if (value === 'ESP32' || value === 'ESP32_LIVE') return 'Physical hardware';
  if (value === 'TEST_READING') return 'Test reading';
  if (value === 'SIMULATED') return 'Simulated';
  if (value === 'NONE') return 'None';
  return value;
}
