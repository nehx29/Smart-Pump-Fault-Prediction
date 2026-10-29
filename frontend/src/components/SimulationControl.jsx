const MODES = [
  { id: 'NORMAL',         label: 'Normal' },
  { id: 'HIGH_PRESSURE',  label: 'High Pressure' },
  { id: 'OVERCURRENT',    label: 'Overcurrent' },
  { id: 'HIGH_VIBRATION', label: 'High Vibration' },
  { id: 'COMBINED_FAULT', label: 'Combined Fault' },
  { id: 'RANDOM_DRIFT',   label: 'Random mix' },
];

export default function SimulationControl({ simMode, onModeChange, isSimRunning, onToggleSim, onSendSingle, isBackendConnected }) {
  return (
    <div className="card sim-panel">
      <div className="card-header">
        <span>Test data generator</span>
        {isSimRunning && <span className="badge badge-simulated">Sending test readings</span>}
      </div>
      <div className="card-body">
        <div className="sim-warning">
          <span>This tool stores synthetic test readings. It is not a physical sensor feed and is not a Wokwi connection.</span>
        </div>

        <div className="sim-modes">
          {MODES.map(m => (
            <button
              key={m.id}
              id={`sim-mode-${m.id}`}
              className={`sim-mode-btn ${simMode === m.id ? 'active' : ''}`}
              onClick={() => onModeChange(m.id)}
              type="button"
            >
              {m.label}
            </button>
          ))}
        </div>

        <div className="sim-controls">
          <button
            id="sim-toggle-btn"
            className={`btn ${isSimRunning ? 'btn-danger' : 'btn-primary'}`}
            onClick={onToggleSim}
            disabled={!isBackendConnected}
            type="button"
          >
            {isSimRunning ? 'Stop test stream' : 'Start test stream'}
          </button>
          <button
            id="sim-send-single-btn"
            className="btn btn-outline"
            onClick={onSendSingle}
            disabled={!isBackendConnected || isSimRunning}
            type="button"
          >
            Send one test reading
          </button>
        </div>
      </div>
    </div>
  );
}
