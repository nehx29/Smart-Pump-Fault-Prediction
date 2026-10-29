import SensorCard from '../components/SensorCard';
import StatusBadge from '../components/StatusBadge';
import AlertBanner from '../components/AlertBanner';
import LiveChart from '../components/LiveChart';
import HistoryTable from '../components/HistoryTable';
import { formatConfidence, formatTimestamp, sourceLabel } from '../utils/format';

export default function DashboardPage({
  latestReading, history, onRefresh,
}) {
  return (
    <>
      <div className="page-header">
        <div className="flex items-center justify-between">
          <div>
            <h2>Overview</h2>
            <p>Most recent reading from the database with the predicted pump condition and trend chart. Not a live sensor stream — click Refresh to load the latest records.</p>
          </div>
          <button className="btn btn-outline btn-sm" onClick={onRefresh}>
            Refresh
          </button>
        </div>
      </div>

      {latestReading && (
        <AlertBanner
          prediction={latestReading.prediction}
          confidence={latestReading.confidence}
          timestamp={latestReading.timestamp}
        />
      )}

      <div className="section">
        <div className="grid-3">
          <SensorCard
            label="Pressure"
            value={latestReading?.pressure}
            unit="bar"
            color="#3d6b8c"
            timestamp={latestReading?.timestamp}
            icon={
              <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>
              </svg>
            }
          />
          <SensorCard
            label="Motor Current"
            value={latestReading?.current}
            unit="A"
            color="#b45309"
            timestamp={latestReading?.timestamp}
            icon={
              <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
              </svg>
            }
          />
          <SensorCard
            label="Vibration"
            value={latestReading?.vibration}
            unit="mm/s"
            color="#3f6f5b"
            timestamp={latestReading?.timestamp}
            icon={
              <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
              </svg>
            }
          />
        </div>
      </div>

      <div className="section">
        <div className="card">
          <div className="card-header">
            <div className="card-header-left">
              <span>Pump Condition</span>
            </div>
          </div>
          <div className="card-body">
            {latestReading ? (
              <div className="prediction-result">
                <div className="prediction-class">
                  <StatusBadge prediction={latestReading.prediction} />
                </div>
                <div className="info-grid mt-md">
                  <div className="info-row">
                    <span className="info-label">Confidence</span>
                    <span className="info-value font-mono" title="How certain the classifier is. Near-100% is expected for readings from known condition ranges.">
                      {formatConfidence(latestReading.confidence)}
                    </span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Last Updated</span>
                    <span className="info-value">{formatTimestamp(latestReading.timestamp)}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Data source</span>
                    <span className="info-value">{sourceLabel(latestReading.data_source)}</span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="empty-state">
                <p>No stored readings yet.</p>
                <p style={{ fontSize: '0.82rem', marginTop: 'var(--space-sm)' }}>
                  Go to <strong>Pump Monitoring</strong> and use the Test Data Generator,
                  or go to <strong>Fault Detection</strong> to evaluate a test reading.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="section">
        <LiveChart data={history} title="Stored sensor readings" />
      </div>

      <div className="section">
        <HistoryTable data={history} maxRows={10} />
      </div>
    </>
  );
}
