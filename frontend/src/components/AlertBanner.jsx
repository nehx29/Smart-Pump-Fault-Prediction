import { formatConfidence, formatTimestamp } from '../utils/format';

export default function AlertBanner({ prediction, confidence, timestamp }) {
  if (!prediction || prediction === 'Normal') return null;

  const isCritical = ['High Pressure Fault', 'Overcurrent Fault', 'Combined Fault'].includes(prediction);
  const severity = isCritical ? 'critical' : 'warning';

  return (
    <div className={`alert-banner ${severity}`}>
      <div className="alert-banner-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
          <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
        </svg>
      </div>
      <div className="alert-banner-content">
        <div className="alert-banner-title">
          {isCritical ? 'Critical fault' : 'Warning'} — {prediction}
        </div>
        <div className="alert-banner-detail">
          Confidence: {formatConfidence(confidence)}
          {timestamp && ` · ${formatTimestamp(timestamp)}`}
        </div>
      </div>
    </div>
  );
}
