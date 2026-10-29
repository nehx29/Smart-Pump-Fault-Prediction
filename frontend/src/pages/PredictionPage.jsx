import { useState } from 'react';
import StatusBadge from '../components/StatusBadge';
import { predictPumpFault, sendSensorData } from '../services/api';
import { formatConfidence, formatNumber, formatTimestamp } from '../utils/format';

export default function PredictionPage({ isBackendConnected, onRefresh }) {
  const [testForm, setTestForm] = useState({ pressure: '', current: '', vibration: '' });
  const [testResult, setTestResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [saveToHistory, setSaveToHistory] = useState(false);

  const parseInputs = () => {
    const pressure = parseFloat(testForm.pressure);
    const current = parseFloat(testForm.current);
    const vibration = parseFloat(testForm.vibration);
    if (![pressure, current, vibration].every(Number.isFinite)) {
      return { error: 'Enter numeric values for pressure, motor current, and vibration.' };
    }
    return { pressure, current, vibration };
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!isBackendConnected) {
      setTestResult({ success: false, error: 'Service is unreachable. Start the backend and try again.' });
      return;
    }

    const parsed = parseInputs();
    if (parsed.error) {
      setTestResult({ success: false, error: parsed.error });
      return;
    }

    setIsLoading(true);
    setTestResult(null);

    try {
      if (saveToHistory) {
        const res = await sendSensorData({
          pressure: parsed.pressure,
          current: parsed.current,
          vibration: parsed.vibration,
          data_source: 'TEST_READING',
        });

        if (res && res.success && res.data) {
          setTestResult({
            success: true,
            prediction: res.data.prediction,
            confidence: res.data.confidence,
            input: {
              pressure: res.data.pressure,
              current: res.data.current,
              vibration: res.data.vibration,
            },
            timestamp: res.data.timestamp,
            explanation: res.data.explanation || res.data.message,
            stored_id: res.data.id,
            source: 'Test reading (stored)',
          });
          if (onRefresh) onRefresh();
        } else {
          setTestResult({
            success: false,
            error: res?.error || 'Failed to evaluate or store the test reading.',
          });
        }
      } else {
        const res = await predictPumpFault({
          pressure: parsed.pressure,
          current: parsed.current,
          vibration: parsed.vibration,
        });

        if (res && res.success && res.prediction) {
          setTestResult({
            success: true,
            prediction: res.prediction,
            confidence: res.confidence,
            input: res.input,
            timestamp: res.timestamp,
            explanation: res.explanation,
            source: 'Test reading (not stored)',
          });
        } else {
          setTestResult({
            success: false,
            error: res?.error || 'Prediction failed.',
          });
        }
      }
    } catch (err) {
      setTestResult({ success: false, error: err.message || 'Request failed.' });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <div className="page-header">
        <h2>Fault Detection</h2>
        <p>
          Evaluate a <strong>test reading</strong>. Entered values are not live sensor measurements.
          The displayed condition and confidence are the actual model outputs for the submitted inputs.
        </p>
      </div>

      <div className="grid-2">
        <div className="card">
          <div className="card-header">
            <span>Test reading</span>
          </div>
          <div className="card-body">
            <div className="note-box info" style={{ marginBottom: 'var(--space-md)' }}>
              Enter sensor values below to see what pump condition they would produce.
              These are test inputs — not live sensor measurements.
            </div>
            <form onSubmit={handleSubmit}>
              <div className="input-group">
                <label htmlFor="pressure-input">Pressure (bar)</label>
                <input
                  id="pressure-input"
                  type="number"
                  step="any"
                  value={testForm.pressure}
                  onChange={e => setTestForm({ ...testForm, pressure: e.target.value })}
                  placeholder="e.g. 3.80"
                  required
                />
              </div>
              <div className="input-group">
                <label htmlFor="current-input">Motor Current (A)</label>
                <input
                  id="current-input"
                  type="number"
                  step="any"
                  value={testForm.current}
                  onChange={e => setTestForm({ ...testForm, current: e.target.value })}
                  placeholder="e.g. 5.03"
                  required
                />
              </div>
              <div className="input-group">
                <label htmlFor="vibration-input">Vibration (mm/s)</label>
                <input
                  id="vibration-input"
                  type="number"
                  step="any"
                  value={testForm.vibration}
                  onChange={e => setTestForm({ ...testForm, vibration: e.target.value })}
                  placeholder="e.g. 1.21"
                  required
                />
              </div>

              <label className="checkbox-row">
                <input
                  type="checkbox"
                  checked={saveToHistory}
                  onChange={e => setSaveToHistory(e.target.checked)}
                />
                Save this test reading to history
              </label>

              <button type="submit" className="btn btn-primary" disabled={isLoading || !isBackendConnected}>
                {isLoading ? 'Evaluating…' : 'Evaluate pump condition'}
              </button>
            </form>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <span>Pump Condition</span>
          </div>
          <div className="card-body">
            {isLoading ? (
              <div className="empty-state">
                <p>Evaluating submitted values…</p>
              </div>
            ) : testResult?.success ? (
              <div>
                <div className="prediction-class">
                  <StatusBadge prediction={testResult.prediction} />
                </div>
                <div className="info-grid mt-md">
                  <div className="info-row">
                    <span className="info-label">Confidence</span>
                    <span className="info-value font-mono" title="How certain the classifier is. Near-100% is expected for well-separated synthetic training data.">{formatConfidence(testResult.confidence)}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Pressure used</span>
                    <span className="info-value font-mono">{formatNumber(testResult.input?.pressure)} bar</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Motor current used</span>
                    <span className="info-value font-mono">{formatNumber(testResult.input?.current)} A</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Vibration used</span>
                    <span className="info-value font-mono">{formatNumber(testResult.input?.vibration)} mm/s</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Last Updated</span>
                    <span className="info-value">{formatTimestamp(testResult.timestamp)}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Reading type</span>
                    <span className="info-value">{testResult.source}</span>
                  </div>
                </div>
                {testResult.explanation && (
                  <div className="note-box warning mt-md">
                    {testResult.explanation}
                  </div>
                )}
                {testResult.stored_id && (
                  <p className="text-sm text-secondary mt-md">Stored as reading #{testResult.stored_id}.</p>
                )}
                {testResult.confidence != null && testResult.confidence >= 0.995 && (
                  <p className="text-sm text-muted mt-md" style={{ fontStyle: 'italic' }}>
                    Near-100% confidence is expected when inputs fall clearly within a known condition range. See the Help page for details.
                  </p>
                )}
              </div>
            ) : testResult && !testResult.success ? (
              <div className="error-banner" style={{ marginBottom: 0 }}>
                <span className="error-banner-text">{testResult.error}</span>
              </div>
            ) : (
              <div className="empty-state">
                <p>Submit a test reading to see the predicted pump condition and confidence.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
