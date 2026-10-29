import SensorCard from '../components/SensorCard';
import LiveChart from '../components/LiveChart';
import SimulationControl from '../components/SimulationControl';
import { formatTimestamp, sourceLabel } from '../utils/format';

// Returns an age-aware status for the latest reading.
function getReadingFreshness(timestamp) {
  if (!timestamp) return null;
  const raw = String(timestamp);
  const iso = raw.endsWith('Z') || raw.includes('+') ? raw : `${raw.replace(' ', 'T')}Z`;
  const ageMs = Date.now() - new Date(iso).getTime();
  if (ageMs < 15000)  return 'just now';
  if (ageMs < 60000)  return `${Math.round(ageMs / 1000)}s ago`;
  if (ageMs < 3600000) return `${Math.round(ageMs / 60000)}m ago`;
  return null; // stale — show full timestamp
}

function DataSourceBadge({ source }) {
  const v = (source || 'NONE').toUpperCase();
  if (v === 'WOKWI_SIMULATED' || v === 'WOKWI') {
    return <span className="badge badge-wokwi">Wokwi simulator</span>;
  }
  if (v === 'ESP32' || v === 'ESP32_LIVE') {
    return <span className="badge badge-esp32">Physical hardware</span>;
  }
  if (v === 'TEST_READING') {
    return <span className="badge badge-info">Test reading</span>;
  }
  if (v === 'SIMULATED') {
    return <span className="badge badge-simulated">Synthetic</span>;
  }
  return <span className="badge badge-info">{source}</span>;
}

export default function SensorMonitoringPage({
  latestReading, history, isBackendConnected, dataSource, onRefresh,
  simMode, onModeChange, isSimRunning, onToggleSim, onSendSingle,
}) {
  const freshness = latestReading?.timestamp ? getReadingFreshness(latestReading.timestamp) : null;
  const isWokwi = latestReading?.data_source === 'WOKWI_SIMULATED' || latestReading?.data_source === 'WOKWI';
  const isHardware = latestReading?.data_source === 'ESP32' || latestReading?.data_source === 'ESP32_LIVE';

  return (
    <>
      <div className="page-header">
        <div className="flex items-center justify-between">
          <div>
            <h2>Pump Monitoring</h2>
            <p>
              Latest stored sensor readings and trend chart.
              Readings may come from the Wokwi simulator, a physical ESP32 board, or the synthetic test generator below.
              Each reading is clearly labelled by source.
            </p>
          </div>
          <button className="btn btn-outline btn-sm" onClick={onRefresh} disabled={!isBackendConnected}>
            Refresh
          </button>
        </div>
      </div>

      {/* Latest reading source banner */}
      {latestReading ? (
        <div className="section">
          <div className={`note-box ${isHardware ? 'success' : isWokwi ? 'info' : 'info'}`}>
            <div className="flex items-center gap-sm flex-wrap">
              <span>Latest stored reading:</span>
              <DataSourceBadge source={latestReading.data_source} />
              <span className="text-muted">·</span>
              <span>
                {freshness
                  ? `Updated ${freshness}`
                  : formatTimestamp(latestReading.timestamp)}
              </span>
              {isHardware && (
                <span className="text-success" style={{ fontSize: '0.78rem' }}>
                  ✓ Real sensor data
                </span>
              )}
              {isWokwi && (
                <span style={{ fontSize: '0.78rem', color: 'var(--accent-purple)' }}>
                  ✓ Wokwi simulator data
                </span>
              )}
            </div>
          </div>
        </div>
      ) : (
        <div className="section">
          <div className="note-box info">
            No readings stored yet. Use the Test Data Generator below or connect a Wokwi simulation.
          </div>
        </div>
      )}

      {/* Sensor cards */}
      <div className="section">
        <div className="grid-3">
          <SensorCard
            label="Pressure"
            value={latestReading?.pressure}
            unit="bar"
            color="#3d6b8c"
            timestamp={latestReading?.timestamp}
            icon={<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>}
          />
          <SensorCard
            label="Motor Current"
            value={latestReading?.current}
            unit="A"
            color="#b45309"
            timestamp={latestReading?.timestamp}
            icon={<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>}
          />
          <SensorCard
            label="Vibration"
            value={latestReading?.vibration}
            unit="mm/s"
            color="#3f6f5b"
            timestamp={latestReading?.timestamp}
            icon={<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>}
          />
        </div>
      </div>

      {/* Trend chart */}
      <div className="section">
        <LiveChart data={history} title="Stored sensor readings" />
      </div>

      {/* Wokwi connection guide */}
      <div className="section">
        <div className="card">
          <div className="card-header">
            <div className="card-header-left">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/>
              </svg>
              <span>Connect Wokwi ESP32 simulator</span>
            </div>
            <span className="badge badge-wokwi">Wokwi simulator</span>
          </div>
          <div className="card-body">
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: 'var(--space-md)', lineHeight: 1.7 }}>
              Wokwi runs in a browser and cannot reach <code>localhost</code> directly.
              A Cloudflare Quick Tunnel creates a temporary public HTTPS URL that bridges Wokwi to your local Flask backend.
            </p>

            <div className="wokwi-steps">
              <div className="wokwi-step">
                <div className="wokwi-step-num">1</div>
                <div className="wokwi-step-body">
                  <div className="wokwi-step-title">Start the backend</div>
                  <code className="wokwi-code">python app.py</code>
                  <div className="wokwi-step-note">Run from the <code>backend/</code> directory. Confirm it starts on port 5000.</div>
                </div>
              </div>

              <div className="wokwi-step">
                <div className="wokwi-step-num">2</div>
                <div className="wokwi-step-body">
                  <div className="wokwi-step-title">Start the Cloudflare tunnel</div>
                  <code className="wokwi-code">cloudflared-windows-amd64.exe tunnel --url http://127.0.0.1:5000</code>
                  <div className="wokwi-step-note">The tunnel prints a URL like <strong>https://xxxx-yyyy-zzzz.trycloudflare.com</strong> — copy it. This URL changes every restart.</div>
                </div>
              </div>

              <div className="wokwi-step">
                <div className="wokwi-step-num">3</div>
                <div className="wokwi-step-body">
                  <div className="wokwi-step-title">Update the sketch</div>
                  <div className="wokwi-step-note">
                    In <code>esp32/wokwi_sketch.ino</code>, replace both URL constants:
                  </div>
                  <code className="wokwi-code">{'CLOUDFLARE_HOST = "https://xxxx-yyyy.trycloudflare.com"'}</code>
                  <code className="wokwi-code" style={{ marginTop: 4 }}>{'SERVER_URL = "https://xxxx-yyyy.trycloudflare.com/api/sensor-data"'}</code>
                </div>
              </div>

              <div className="wokwi-step">
                <div className="wokwi-step-num">4</div>
                <div className="wokwi-step-body">
                  <div className="wokwi-step-title">Add potentiometers in Wokwi diagram</div>
                  <div className="wokwi-step-note">
                    Connect potentiometers to <strong>GPIO 34</strong> (Pressure), <strong>GPIO 35</strong> (Current), <strong>GPIO 32</strong> (Vibration).
                    Use the <code>esp32/diagram.json</code> file or the reference table below.
                  </div>
                  <div className="wokwi-slider-table">
                    <div className="wokwi-slider-row header">
                      <span>Condition</span>
                      <span>GPIO 34 Pressure</span>
                      <span>GPIO 35 Current</span>
                      <span>GPIO 32 Vibration</span>
                    </div>
                    {[
                      ['Normal',                   '~25%  (3.8 bar)', '~20%  (5.0 A)', '~6%   (1.2 mm/s)'],
                      ['High Pressure Fault',      '~45%  (6.8 bar)', '~26%  (6.5 A)', '~14%  (2.8 mm/s)'],
                      ['Overcurrent Fault',        '~22%  (3.3 bar)', '~37%  (9.3 A)', '~17%  (3.4 mm/s)'],
                      ['Excessive Vibration',      '~24%  (3.6 bar)', '~22%  (5.5 A)', '~34%  (6.8 mm/s)'],
                      ['Combined Fault',           '~8%   (1.2 bar)', '~34%  (8.5 A)', '~38%  (7.6 mm/s)'],
                    ].map(([cond, p, c, v]) => (
                      <div key={cond} className="wokwi-slider-row">
                        <span>{cond}</span>
                        <span className="font-mono">{p}</span>
                        <span className="font-mono">{c}</span>
                        <span className="font-mono">{v}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="wokwi-step">
                <div className="wokwi-step-num">5</div>
                <div className="wokwi-step-body">
                  <div className="wokwi-step-title">Run the simulation</div>
                  <div className="wokwi-step-note">
                    Click <strong>Run</strong> in Wokwi. The serial monitor should show HTTP 201 responses.
                    Click <strong>Refresh</strong> on this page — readings labelled <strong>Wokwi simulator</strong> will appear above.
                  </div>
                </div>
              </div>
            </div>

            <div className="note-box warning" style={{ marginTop: 'var(--space-md)' }}>
              <strong>Quick tunnels expire</strong> when you restart cloudflared. You must update the sketch URL and restart the Wokwi simulation each session. See <code>TUNNEL_SETUP.md</code> for the full workflow and troubleshooting guide.
            </div>
          </div>
        </div>
      </div>

      {/* Synthetic test data generator */}
      <div className="section">
        <SimulationControl
          simMode={simMode}
          onModeChange={onModeChange}
          isSimRunning={isSimRunning}
          onToggleSim={onToggleSim}
          onSendSingle={onSendSingle}
          isBackendConnected={isBackendConnected}
        />
      </div>
    </>
  );
}
