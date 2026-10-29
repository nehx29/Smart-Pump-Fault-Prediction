export default function HelpPage() {
  return (
    <>
      <div className="page-header">
        <h2>How to Use This System</h2>
        <p>A quick guide to understanding each page, the sensor readings, and what the results mean.</p>
      </div>

      {/* What this system does */}
      <div className="card section">
        <div className="card-header">
          <span>What this system does</span>
        </div>
        <div className="card-body">
          <p style={{ fontSize: '0.9rem', lineHeight: 1.8, color: 'var(--text-secondary)', marginBottom: 'var(--space-md)' }}>
            This application monitors the health of a centrifugal pump by reading three sensor signals —
            discharge pressure, motor current draw, and bearing vibration — and classifying the pump's
            operating condition into one of five states: <strong>Normal</strong>, <strong>High Pressure Fault</strong>,{' '}
            <strong>Overcurrent Fault</strong>, <strong>Excessive Vibration Fault</strong>, or <strong>Combined Fault</strong>.
          </p>
          <p style={{ fontSize: '0.9rem', lineHeight: 1.8, color: 'var(--text-secondary)' }}>
            Readings can come from a physical ESP32 sensor board, from the Wokwi browser simulator,
            or from manually entered test values. All readings are stored in a local database and
            are visible in the history and alerts pages.
          </p>
        </div>
      </div>

      {/* Pages explained */}
      <div className="card section">
        <div className="card-header">
          <span>Pages explained</span>
        </div>
        <div className="card-body">
          <div className="help-page-list">

            <div className="help-page-item">
              <div className="help-page-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>
              </div>
              <div className="help-page-content">
                <div className="help-page-title">Overview</div>
                <div className="help-page-desc">
                  Shows the most recent sensor reading stored in the database — pressure, motor current,
                  and vibration values — along with the predicted pump condition and a trend chart of the
                  last 30 readings. This is the starting point for checking current pump status at a glance.
                  The readings shown here come from the database, not from a live sensor stream.
                </div>
              </div>
            </div>

            <div className="help-page-item">
              <div className="help-page-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
              </div>
              <div className="help-page-content">
                <div className="help-page-title">Pump Monitoring</div>
                <div className="help-page-desc">
                  Displays the same sensor readings as the Overview but also includes the <strong>Test Data Generator</strong>.
                  Use the generator to send synthetic test readings to the database — choose a condition mode
                  such as Normal or High Pressure, then click <em>Send one test reading</em> or start a
                  continuous stream. This is useful for testing the system without physical hardware.
                  The generator clearly labels all readings as synthetic.
                </div>
              </div>
            </div>

            <div className="help-page-item">
              <div className="help-page-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
              </div>
              <div className="help-page-content">
                <div className="help-page-title">Fault Detection</div>
                <div className="help-page-desc">
                  Lets you enter specific sensor values and instantly see what condition the system predicts.
                  Enter a pressure reading in bar, a motor current in amps, and a vibration level in mm/s,
                  then click <em>Evaluate pump condition</em>. You can optionally save the reading to history.
                  Use this page to verify that a specific set of readings would be correctly classified.
                  These are test inputs — they are not measurements from a real sensor unless you manually
                  enter real hardware values.
                </div>
              </div>
            </div>

            <div className="help-page-item">
              <div className="help-page-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
              </div>
              <div className="help-page-content">
                <div className="help-page-title">Reading History</div>
                <div className="help-page-desc">
                  Shows all stored readings in reverse chronological order. You can filter by data source
                  (e.g. show only ESP32 hardware readings), change how many records are loaded, and
                  export the table to a CSV file. Each row shows the sensor values, predicted condition,
                  confidence, and source.
                </div>
              </div>
            </div>

            <div className="help-page-item">
              <div className="help-page-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
              </div>
              <div className="help-page-content">
                <div className="help-page-title">Alerts</div>
                <div className="help-page-desc">
                  Lists fault events derived from stored readings. Only readings with a non-Normal
                  prediction are shown by default. Each alert card shows the fault type, severity
                  (Warning or Critical), the sensor values that triggered it, and a recommended
                  inspection action. Toggle <em>Showing faults only</em> to also see Normal readings.
                  Alerts are not pushed in real time — they are derived from the database on demand.
                </div>
              </div>
            </div>

          </div>
        </div>
      </div>

      {/* Sensor readings explained */}
      <div className="card section">
        <div className="card-header">
          <span>Sensor readings explained</span>
        </div>
        <div className="card-body">
          <div className="help-sensor-grid">

            <div className="help-sensor-item">
              <div className="help-sensor-label" style={{ color: 'var(--color-pressure)' }}>Pressure</div>
              <div className="help-sensor-unit">bar</div>
              <div className="help-sensor-desc">
                The pressure at the pump's discharge outlet. Normal range is roughly 3.5 – 4.5 bar.
                Values above ~5.5 bar suggest a blockage or restriction downstream.
                Values below ~2 bar can indicate cavitation (the pump is drawing in air).
              </div>
              <div className="help-sensor-ranges">
                <span className="help-range normal">Normal: 2.5 – 4.8 bar</span>
                <span className="help-range fault">High fault: &gt; 5.5 bar</span>
                <span className="help-range fault">Low (cavitation): &lt; 2.0 bar</span>
              </div>
            </div>

            <div className="help-sensor-item">
              <div className="help-sensor-label" style={{ color: 'var(--color-current)' }}>Motor Current</div>
              <div className="help-sensor-unit">A (amperes)</div>
              <div className="help-sensor-desc">
                The electrical current drawn by the pump motor. Normal range is roughly 4.5 – 5.5 A.
                Higher current means the motor is working harder — this can indicate a mechanical
                obstruction, impeller damage, or electrical overload.
              </div>
              <div className="help-sensor-ranges">
                <span className="help-range normal">Normal: 3.5 – 6.2 A</span>
                <span className="help-range fault">Overcurrent fault: &gt; 8.0 A</span>
              </div>
            </div>

            <div className="help-sensor-item">
              <div className="help-sensor-label" style={{ color: 'var(--color-vibration)' }}>Vibration</div>
              <div className="help-sensor-unit">mm/s (RMS velocity)</div>
              <div className="help-sensor-desc">
                The vibration measured at the pump's bearing housing. Low vibration means smooth
                mechanical operation. High vibration indicates bearing wear, shaft misalignment,
                impeller imbalance, or cavitation.
              </div>
              <div className="help-sensor-ranges">
                <span className="help-range normal">Normal: 0.4 – 2.2 mm/s</span>
                <span className="help-range fault">High vibration fault: &gt; 4.8 mm/s</span>
              </div>
            </div>

          </div>
        </div>
      </div>

      {/* Result fields explained */}
      <div className="card section">
        <div className="card-header">
          <span>Result fields explained</span>
        </div>
        <div className="card-body">
          <div className="help-field-list">

            <div className="help-field-item">
              <div className="help-field-name">Predicted Condition</div>
              <div className="help-field-desc">
                The pump operating state classified from the three sensor readings.
                Possible values: <strong>Normal</strong>, <strong>High Pressure Fault</strong>,{' '}
                <strong>Overcurrent Fault</strong>, <strong>Excessive Vibration Fault</strong>,{' '}
                <strong>Combined Fault</strong>.
              </div>
            </div>

            <div className="help-field-item">
              <div className="help-field-name">Confidence</div>
              <div className="help-field-desc">
                How certain the classifier is about the predicted condition, expressed as a percentage.
                This system is trained on synthetically generated data with clearly separated fault
                classes, so near-100% confidence is expected and normal for readings that fall
                squarely within a known condition range. A reading near a boundary between two
                conditions may produce lower confidence.
                <div className="note-box info" style={{ marginTop: 'var(--space-sm)', fontSize: '0.78rem' }}>
                  High confidence does not guarantee the pump is healthy — it means the classifier
                  matched the input pattern strongly. Always combine this with the predicted
                  condition label and the actual sensor values.
                </div>
              </div>
            </div>

            <div className="help-field-item">
              <div className="help-field-name">Data Source</div>
              <div className="help-field-desc">
                Where the reading came from:
                <ul style={{ marginTop: 'var(--space-xs)', paddingLeft: 'var(--space-lg)', lineHeight: 2 }}>
                  <li><strong>Simulated</strong> — values generated by the in-browser test data generator.</li>
                  <li><strong>Test reading</strong> — values you entered manually in the Fault Detection page.</li>
                  <li><strong>Wokwi simulator</strong> — values sent from the Wokwi ESP32 browser simulation.</li>
                  <li><strong>Physical hardware</strong> — values from a real ESP32 sensor board connected over Wi-Fi.</li>
                </ul>
                Only readings labelled <em>Physical hardware</em> represent real sensor measurements.
              </div>
            </div>

            <div className="help-field-item">
              <div className="help-field-name">Last Updated</div>
              <div className="help-field-desc">
                The UTC timestamp when the reading was saved to the database. The dashboard shows
                the most recently stored reading — this is not a live stream. Refresh the page
                to load the latest records.
              </div>
            </div>

          </div>
        </div>
      </div>

      {/* Fault conditions explained */}
      <div className="card section">
        <div className="card-header">
          <span>Fault conditions explained</span>
        </div>
        <div className="card-body">
          <div className="help-fault-list">

            {[
              {
                name: 'Normal',
                color: 'var(--color-success)',
                severity: 'No fault',
                desc: 'All three sensor readings are within the expected operating range. The pump is running normally. No action required.',
              },
              {
                name: 'High Pressure Fault',
                color: 'var(--accent-amber)',
                severity: 'Warning',
                desc: 'Discharge pressure is above the normal operating envelope. Possible causes: blocked or partially closed outlet valve, downstream restriction, pump running against a closed system.',
              },
              {
                name: 'Overcurrent Fault',
                color: 'var(--accent-amber)',
                severity: 'Warning',
                desc: 'Motor current draw exceeds the normal range. Possible causes: mechanical obstruction inside the pump, impeller damage, cavitation, or electrical overload.',
              },
              {
                name: 'Excessive Vibration Fault',
                color: 'var(--accent-amber)',
                severity: 'Warning',
                desc: 'Bearing vibration velocity is above the normal threshold. Possible causes: bearing wear, shaft misalignment, impeller imbalance, or loose mounting.',
              },
              {
                name: 'Combined Fault',
                color: 'var(--accent-red)',
                severity: 'Critical',
                desc: 'Multiple sensor signals are simultaneously outside normal ranges — typically low pressure with high current and high vibration. This pattern suggests severe pump distress such as cavitation with mechanical damage. Requires immediate inspection.',
              },
            ].map(fault => (
              <div key={fault.name} className="help-fault-item" style={{ borderLeftColor: fault.color }}>
                <div className="help-fault-header">
                  <span className="help-fault-name" style={{ color: fault.color }}>{fault.name}</span>
                  <span className="help-fault-severity">{fault.severity}</span>
                </div>
                <div className="help-fault-desc">{fault.desc}</div>
              </div>
            ))}

          </div>
        </div>
      </div>

      {/* Hardware connection */}
      <div className="card section">
        <div className="card-header">
          <span>Connecting real hardware or Wokwi</span>
        </div>
        <div className="card-body">
          <div style={{ fontSize: '0.88rem', lineHeight: 1.8, color: 'var(--text-secondary)' }}>
            <p style={{ marginBottom: 'var(--space-md)' }}>
              <strong style={{ color: 'var(--text-primary)' }}>Physical ESP32 (local network):</strong>{' '}
              Flash <code>esp32/pump_sensor.ino</code> to your ESP32 board, set the <code>SERVER_URL</code>
              constant to <code>http://&lt;your-computer-ip&gt;:5000/api/sensor-data</code>,
              and connect the board to the same Wi-Fi network as the server. Readings will appear
              labelled <em>Physical hardware</em>.
            </p>
            <p style={{ marginBottom: 'var(--space-md)' }}>
              <strong style={{ color: 'var(--text-primary)' }}>Wokwi browser simulator:</strong>{' '}
              Open <code>esp32/wokwi_sketch.ino</code> in the Wokwi simulator. Because Wokwi runs in
              a browser, it cannot reach <code>localhost</code> directly. You need to start a
              Cloudflare Quick Tunnel (<code>cloudflared tunnel --url http://localhost:5000</code>),
              copy the generated public URL, and paste it into the <code>CLOUDFLARE_HOST</code>
              and <code>SERVER_URL</code> constants before running the simulation. Readings will
              appear labelled <em>Wokwi simulator</em>.
            </p>
            <p>
              <strong style={{ color: 'var(--text-primary)' }}>No hardware:</strong>{' '}
              Use the Test Data Generator on the Pump Monitoring page to send synthetic readings,
              or enter values manually on the Fault Detection page.
            </p>
          </div>
        </div>
      </div>
    </>
  );
}
