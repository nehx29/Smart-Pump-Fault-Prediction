import StatusBadge from './StatusBadge';

const SOURCE_BADGES = {
  SIMULATED: 'badge-simulated',
  ESP32: 'badge-esp32',
  WOKWI: 'badge-wokwi',
  WOKWI_SIMULATED: 'badge-wokwi',
  TEST_READING: 'badge-info',
};

export default function HistoryTable({ data, maxRows = 10 }) {
  if (!data || data.length === 0) {
    return (
      <div className="card">
        <div className="card-header">
          <div className="card-header-left">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/>
            </svg>
            <span>Recent readings</span>
          </div>
        </div>
        <div className="card-body">
          <div className="empty-state">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/>
            </svg>
            <p>No stored readings yet</p>
          </div>
        </div>
      </div>
    );
  }

  const rows = data.slice(0, maxRows);

  return (
    <div className="card">
      <div className="card-header">
        <div className="card-header-left">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/>
          </svg>
          <span>Recent Readings</span>
        </div>
        <span className="text-xs text-muted">Last {rows.length} of {data.length}</span>
      </div>
      <div style={{ overflowX: 'auto' }}>
        <table className="data-table">
          <thead>
            <tr>
              <th>Time</th>
              <th>Pressure</th>
              <th>Motor Current</th>
              <th>Vibration</th>
              <th>Pump Condition</th>
              <th>Source</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => {
              const ts = row.timestamp
                ? new Date(row.timestamp + (row.timestamp.endsWith('Z') ? '' : 'Z')).toLocaleTimeString()
                : '--';
              const src = row.data_source || 'UNKNOWN';
              const srcClass = SOURCE_BADGES[src] || 'badge-info';

              return (
                <tr key={row.id || i}>
                  <td className="mono">{ts}</td>
                  <td className="mono">{row.pressure != null ? Number(row.pressure).toFixed(2) : '--'}</td>
                  <td className="mono">{row.current != null ? Number(row.current).toFixed(2) : '--'}</td>
                  <td className="mono">{row.vibration != null ? Number(row.vibration).toFixed(2) : '--'}</td>
                  <td><StatusBadge prediction={row.prediction} /></td>
                  <td><span className={`badge ${srcClass}`}>{src}</span></td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
