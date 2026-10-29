import { formatConfidence } from '../utils/format';

const CLASS_MAP = {
  'Normal': 'badge-normal',
  'High Pressure Fault': 'badge-critical',
  'Overcurrent Fault': 'badge-critical',
  'Excessive Vibration Fault': 'badge-warning',
  'Combined Fault': 'badge-critical',
};

export default function StatusBadge({ prediction, confidence, showConfidence = false }) {
  if (!prediction) {
    return <span className="badge badge-info">Unknown</span>;
  }

  const cls = CLASS_MAP[prediction] || 'badge-info';

  return (
    <span className={`badge ${cls}`}>
      {prediction}
      {showConfidence && confidence != null && (
        <span style={{ marginLeft: 6, opacity: 0.85 }}>
          {formatConfidence(confidence)}
        </span>
      )}
    </span>
  );
}
