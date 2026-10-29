import { useState, useEffect, useCallback } from 'react';
import { getAlerts } from '../services/api';
import { formatConfidence, formatNumber, formatTimestamp, sourceLabel } from '../utils/format';

const SEVERITY_CLASS = {
  CRITICAL: 'severity-critical',
  WARNING: 'severity-warning',
  NORMAL: 'severity-normal',
};

export default function AlertsPage() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [faultsOnly, setFaultsOnly] = useState(true);

  const fetchAlertData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getAlerts(100, faultsOnly);
      if (res.success) {
        setAlerts(res.data || []);
      } else {
        setError(res.error || 'Failed to load alerts');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [faultsOnly]);

  useEffect(() => {
    fetchAlertData();
  }, [fetchAlertData]);

  const criticalCount = alerts.filter(a => a.severity === 'CRITICAL').length;
  const warningCount = alerts.filter(a => a.severity === 'WARNING').length;

  return (
    <>
      <div className="page-header">
        <div className="flex items-center justify-between flex-wrap gap-md">
          <div>
            <h2>Alerts</h2>
            <p>Fault events derived from stored readings. Only readings with a non-Normal prediction are shown by default. These are not real-time push notifications.</p>
          </div>
          <div className="controls-row" style={{ marginBottom: 0 }}>
            <button className="btn btn-outline btn-sm" onClick={() => setFaultsOnly(v => !v)}>
              {faultsOnly ? 'Showing faults only' : 'Showing all readings'}
            </button>
            <button className="btn btn-outline btn-sm" onClick={fetchAlertData}>Refresh</button>
          </div>
        </div>
      </div>

      {alerts.length > 0 && (
        <div className="stats-row">
          <div className="stat-item">
            <div className="stat-value">{alerts.length}</div>
            <div className="stat-label">Shown</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">{criticalCount}</div>
            <div className="stat-label">Critical</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">{warningCount}</div>
            <div className="stat-label">Warning</div>
          </div>
        </div>
      )}

      {loading ? (
        <div className="card"><div className="empty-state"><p>Loading alerts from stored readings…</p></div></div>
      ) : error ? (
        <div className="error-banner">
          <span className="error-banner-text">{error}</span>
        </div>
      ) : alerts.length === 0 ? (
        <div className="card">
          <div className="empty-state">
            <p>
              {faultsOnly
                ? 'No fault conditions are present in the current stored readings.'
                : 'No stored readings are available to derive alerts from.'}
            </p>
          </div>
        </div>
      ) : (
        alerts.map(alert => (
          <div key={alert.id} className={`alert-card ${SEVERITY_CLASS[alert.severity] || 'severity-warning'}`}>
            <div className="alert-card-header">
              <div className="alert-card-title">{alert.prediction}</div>
              <span className="text-xs text-muted">{formatConfidence(alert.confidence)}</span>
            </div>
            <div className="alert-card-body">{alert.message}</div>
            <div className="alert-card-readings">
              <span>Pressure {formatNumber(alert.pressure)} bar</span>
              <span>Motor Current {formatNumber(alert.current)} A</span>
              <span>Vibration {formatNumber(alert.vibration)} mm/s</span>
              <span>{sourceLabel(alert.data_source)}</span>
              <span>{formatTimestamp(alert.timestamp)}</span>
            </div>
            {alert.maintenance && alert.is_fault && (
              <div className="maintenance-section">
                <strong>Recommended inspection</strong>
                {alert.maintenance}
              </div>
            )}
          </div>
        ))
      )}
    </>
  );
}
