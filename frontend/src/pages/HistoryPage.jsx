import { useState, useEffect, useCallback } from 'react';
import StatusBadge from '../components/StatusBadge';
import { getHistory } from '../services/api';
import { formatConfidence, formatNumber, formatTimestamp, sourceLabel } from '../utils/format';

const PAGE_SIZE = 20;

export default function HistoryPage() {
  const [allRecords, setAllRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(0);
  const [limit, setLimit] = useState(100);
  const [filterSource, setFilterSource] = useState('ALL');

  const loadHistory = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getHistory(limit);
      if (res && res.success) {
        setAllRecords(res.data || []);
      } else {
        setError(res?.error || 'Failed to load history from the database.');
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [limit]);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  const filtered = filterSource === 'ALL'
    ? allRecords
    : allRecords.filter(r => r.data_source === filterSource);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const pageRecords = filtered.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);

  const exportCSV = () => {
    if (filtered.length === 0) return;
    const headers = ['ID', 'Timestamp', 'Pressure (bar)', 'Motor Current (A)', 'Vibration (mm/s)', 'Data Source', 'Pump Condition', 'Confidence'];
    const rows = filtered.map(r => [
      r.id,
      r.timestamp,
      r.pressure ?? '',
      r.current ?? '',
      r.vibration ?? '',
      r.data_source ?? '',
      r.prediction ?? '',
      r.confidence != null ? formatConfidence(r.confidence) : '',
    ]);
    const csv = [headers, ...rows].map(row => row.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `pump_history_${new Date().toISOString().slice(0, 19).replace(/[T:]/g, '-')}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const uniqueSources = ['ALL', ...new Set(allRecords.map(r => r.data_source).filter(Boolean))];

  return (
    <>
      <div className="page-header">
        <div className="flex items-center justify-between flex-wrap gap-md">
          <div>
            <h2>Reading History</h2>
            <p>All stored sensor readings from the database, newest first. Filter by source or export to CSV. Readings labelled <strong>Physical hardware</strong> are from a real ESP32 board.</p>
          </div>
          <div className="controls-row" style={{ marginBottom: 0 }}>
            <select
              value={filterSource}
              onChange={e => { setFilterSource(e.target.value); setPage(0); }}
            >
              {uniqueSources.map(s => (
                <option key={s} value={s}>{s === 'ALL' ? 'All sources' : sourceLabel(s)}</option>
              ))}
            </select>
            <select
              value={limit}
              onChange={e => { setLimit(Number(e.target.value)); setPage(0); }}
            >
              {[50, 100, 200, 500].map(n => (
                <option key={n} value={n}>Last {n}</option>
              ))}
            </select>
            <button className="btn btn-outline btn-sm" onClick={loadHistory}>Refresh</button>
            <button className="btn btn-outline btn-sm" onClick={exportCSV} disabled={filtered.length === 0}>
              Export CSV
            </button>
          </div>
        </div>
      </div>

      {!loading && !error && allRecords.length > 0 && (
        <div className="stats-row">
          <div className="stat-item">
            <div className="stat-value">{allRecords.length}</div>
            <div className="stat-label">Stored readings</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">{filtered.filter(r => r.prediction && r.prediction !== 'Normal').length}</div>
            <div className="stat-label">Fault readings</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">{filtered.filter(r => r.prediction === 'Normal').length}</div>
            <div className="stat-label">Normal readings</div>
          </div>
        </div>
      )}

      <div className="card">
        <div className="card-header">
          <span>Database records</span>
          {!loading && !error && <span className="text-xs text-muted">Page {page + 1} of {totalPages}</span>}
        </div>
        {loading ? (
          <div className="empty-state"><p>Loading records from the database…</p></div>
        ) : error ? (
          <div className="card-body">
            <div className="error-banner" style={{ marginBottom: 0 }}>
              <span className="error-banner-text">{error}</span>
            </div>
          </div>
        ) : filtered.length === 0 ? (
          <div className="empty-state">
            <p>
              {filterSource !== 'ALL'
                ? `No stored readings for source “${sourceLabel(filterSource)}”.`
                : 'No readings are stored yet. Evaluate a test reading or ingest sensor data through the API.'}
            </p>
          </div>
        ) : (
          <>
            <div style={{ overflowX: 'auto' }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Last Updated</th>
                    <th>Pressure</th>
                    <th>Motor Current</th>
                    <th>Vibration</th>
                    <th>Source</th>
                    <th>Pump Condition</th>
                    <th>Confidence</th>
                  </tr>
                </thead>
                <tbody>
                  {pageRecords.map(row => (
                    <tr key={row.id}>
                      <td className="mono">#{row.id}</td>
                      <td className="mono">{formatTimestamp(row.timestamp)}</td>
                      <td className="mono">{formatNumber(row.pressure)}</td>
                      <td className="mono">{formatNumber(row.current)}</td>
                      <td className="mono">{formatNumber(row.vibration)}</td>
                      <td>{sourceLabel(row.data_source)}</td>
                      <td><StatusBadge prediction={row.prediction} /></td>
                      <td className="mono">{formatConfidence(row.confidence)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {totalPages > 1 && (
              <div className="pagination">
                <button className="btn btn-outline btn-sm" onClick={() => setPage(p => Math.max(0, p - 1))} disabled={page === 0}>Previous</button>
                <span className="pagination-info">{page + 1} / {totalPages}</span>
                <button className="btn btn-outline btn-sm" onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))} disabled={page >= totalPages - 1}>Next</button>
              </div>
            )}
          </>
        )}
      </div>
    </>
  );
}
