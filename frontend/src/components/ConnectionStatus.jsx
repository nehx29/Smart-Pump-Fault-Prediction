export default function ConnectionStatus({ health, isBackendConnected, latestReading, dataSource }) {
  const getDataFreshness = () => {
    if (!latestReading?.timestamp) return { status: 'unknown', label: 'No Data' };
    const ageMs = Date.now() - new Date(latestReading.timestamp + 'Z').getTime();
    if (ageMs < 30000) return { status: 'connected', label: 'Active' };
    if (ageMs < 300000) return { status: 'stale', label: 'Stale' };
    return { status: 'disconnected', label: 'Inactive' };
  };

  const freshness = getDataFreshness();

  const getSourceBadge = () => {
    if (!dataSource || dataSource === 'NONE') return <span className="badge badge-info">None</span>;
    if (dataSource === 'SIMULATED') return <span className="badge badge-simulated">Simulated</span>;
    if (dataSource === 'ESP32') return <span className="badge badge-esp32">ESP32</span>;
    if (dataSource.includes('WOKWI')) return <span className="badge badge-wokwi">Wokwi</span>;
    return <span className="badge badge-info">{dataSource}</span>;
  };

  return (
    <div className="card">
      <div className="card-header">
        <div className="card-header-left">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M5 12.55a11 11 0 0 1 14.08 0"/><path d="M1.42 9a16 16 0 0 1 21.16 0"/><path d="M8.53 16.11a6 6 0 0 1 6.95 0"/><circle cx="12" cy="20" r="1"/>
          </svg>
          <span>System Status</span>
        </div>
      </div>
      <div className="card-body-compact">
        <div className="connection-grid">
          <div className="connection-item">
            <span className={`status-dot ${isBackendConnected ? 'connected' : 'disconnected'}`}></span>
            <div className="connection-item-info">
              <div className="connection-item-label">Monitoring Service</div>
              <div className="connection-item-value" style={{ color: isBackendConnected ? 'var(--color-success)' : 'var(--color-danger)' }}>
                {isBackendConnected ? 'Reachable' : 'Unreachable'}
              </div>
            </div>
          </div>

          <div className="connection-item">
            <span className={`status-dot ${health?.model_loaded ? 'connected' : 'disconnected'}`}></span>
            <div className="connection-item-info">
              <div className="connection-item-label">Fault Detection</div>
              <div className="connection-item-value" style={{ color: health?.model_loaded ? 'var(--color-success)' : 'var(--color-danger)' }}>
                {health?.model_loaded ? 'Ready' : 'Unavailable'}
              </div>
            </div>
          </div>

          <div className="connection-item">
            <span className={`status-dot ${freshness.status}`}></span>
            <div className="connection-item-info">
              <div className="connection-item-label">Sensor Data</div>
              <div className="connection-item-value" style={{
                color: freshness.status === 'connected' ? 'var(--color-success)'
                  : freshness.status === 'stale' ? 'var(--color-warning)'
                  : 'var(--text-muted)'
              }}>
                {freshness.label}
              </div>
            </div>
          </div>

          <div className="connection-item">
            <span className="status-dot unknown" style={{
              background: dataSource && dataSource !== 'NONE' ? 'var(--accent-blue)' : undefined
            }}></span>
            <div className="connection-item-info">
              <div className="connection-item-label">Data Source</div>
              <div className="connection-item-value">{getSourceBadge()}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
