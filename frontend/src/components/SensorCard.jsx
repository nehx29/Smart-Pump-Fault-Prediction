export default function SensorCard({ label, value, unit, icon, color, timestamp }) {
  return (
    <div className="card">
      <div className="sensor-card">
        <div className="sensor-card-icon" style={{ color }}>
          {icon}
        </div>
        <div>
          <span className="sensor-value" style={{ color }}>
            {value != null ? Number(value).toFixed(2) : '--'}
          </span>
          <span className="sensor-unit">{unit}</span>
        </div>
        <div className="sensor-label">{label}</div>
        <div className="sensor-timestamp">
          {timestamp ? new Date(timestamp + (timestamp.endsWith('Z') ? '' : 'Z')).toLocaleString() : 'No data received'}
        </div>
      </div>
    </div>
  );
}
