import { useState, useEffect, useRef, useCallback } from 'react';
import './index.css';

import { getHealth, getLatest, getHistory, sendSensorData } from './services/api';

import Header from './components/Header';
import Footer from './components/Footer';
import DashboardPage from './pages/DashboardPage';
import SensorMonitoringPage from './pages/SensorMonitoringPage';
import PredictionPage from './pages/PredictionPage';
import HistoryPage from './pages/HistoryPage';
import AlertsPage from './pages/AlertsPage';
import HelpPage from './pages/HelpPage';

const SIM_RANGES = {
  NORMAL:         { pressure: [3.2, 4.3],  current: [4.2, 5.8],   vibration: [0.6, 1.8] },
  HIGH_PRESSURE:  { pressure: [5.8, 7.5],  current: [6.0, 7.8],   vibration: [2.0, 3.5] },
  OVERCURRENT:    { pressure: [2.8, 4.2],  current: [8.8, 11.2],  vibration: [2.2, 4.2] },
  HIGH_VIBRATION: { pressure: [3.0, 4.5],  current: [4.8, 6.5],   vibration: [5.5, 8.8] },
  COMBINED_FAULT: { pressure: [1.0, 2.2],  current: [7.5, 9.8],   vibration: [6.0, 9.2] },
};

function rand(min, max) {
  return +(min + Math.random() * (max - min)).toFixed(2);
}

function generateSimValues(mode) {
  let effectiveMode = mode;
  if (mode === 'RANDOM_DRIFT') {
    const modes = Object.keys(SIM_RANGES);
    effectiveMode = modes[Math.floor(Math.random() * modes.length)];
  }
  const r = SIM_RANGES[effectiveMode] || SIM_RANGES.NORMAL;
  return {
    pressure:  rand(r.pressure[0], r.pressure[1]),
    current:   rand(r.current[0], r.current[1]),
    vibration: rand(r.vibration[0], r.vibration[1]),
    data_source: 'SIMULATED',
  };
}

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [latestReading, setLatestReading] = useState(null);
  const [history, setHistory] = useState([]);
  const [health, setHealth] = useState({ status: 'unknown' });
  const [isBackendConnected, setIsBackendConnected] = useState(false);
  const [simMode, setSimMode] = useState('NORMAL');
  const [isSimRunning, setIsSimRunning] = useState(false);
  const [dataSource, setDataSource] = useState('NONE');
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState(null);
  const fetchInProgress = useRef(false);

  const fetchData = useCallback(async () => {
    if (fetchInProgress.current) return;
    fetchInProgress.current = true;
    try {
      const [healthRes, latestRes, historyRes] = await Promise.all([
        getHealth(),
        getLatest(),
        getHistory(30),
      ]);

      setHealth(healthRes);
      const reachable = healthRes.status === 'ok';
      setIsBackendConnected(reachable);
      setLoadError(reachable ? null : 'Service health check failed.');

      if (latestRes.success !== false && latestRes.data) {
        setLatestReading(latestRes.data);
        setDataSource(latestRes.data.data_source || 'UNKNOWN');
      } else if (latestRes.success && !latestRes.data) {
        setLatestReading(null);
        setDataSource('NONE');
      }

      if (historyRes.success !== false && Array.isArray(historyRes.data)) {
        setHistory(historyRes.data);
      }
    } catch {
      setIsBackendConnected(false);
      setHealth({ status: 'error' });
      setLoadError('Unable to reach the monitoring service.');
    } finally {
      fetchInProgress.current = false;
      setIsLoading(false);
    }
  }, []);

  const refreshLatest = useCallback(async () => {
    try {
      const [latestRes, historyRes] = await Promise.all([
        getLatest(),
        getHistory(30),
      ]);
      if (latestRes.success !== false && latestRes.data) {
        setLatestReading(latestRes.data);
        setDataSource(latestRes.data.data_source || 'UNKNOWN');
      } else if (latestRes.success && !latestRes.data) {
        setLatestReading(null);
        setDataSource('NONE');
      }
      if (historyRes.success !== false && Array.isArray(historyRes.data)) {
        setHistory(historyRes.data);
      }
    } catch {
      /* keep last known stored values */
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  useEffect(() => {
    const id = setInterval(async () => {
      try {
        const h = await getHealth();
        setHealth(h);
        setIsBackendConnected(h.status === 'ok');
      } catch {
        setIsBackendConnected(false);
      }
    }, 15000);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    if (isSimRunning) return;
    const id = setInterval(refreshLatest, 5000);
    return () => clearInterval(id);
  }, [isSimRunning, refreshLatest]);

  useEffect(() => {
    if (!isSimRunning || !isBackendConnected) return;

    const id = setInterval(async () => {
      if (fetchInProgress.current) return;
      fetchInProgress.current = true;
      try {
        const values = generateSimValues(simMode);
        await sendSensorData(values);
        await refreshLatest();
      } catch {
        /* do not invent readings on failure */
      } finally {
        fetchInProgress.current = false;
      }
    }, 3000);

    return () => clearInterval(id);
  }, [isSimRunning, isBackendConnected, simMode, refreshLatest]);

  const handleSendSingle = useCallback(async () => {
    if (!isBackendConnected) return;
    const values = generateSimValues(simMode);
    const res = await sendSensorData(values);
    if (res?.success) {
      await refreshLatest();
    }
  }, [isBackendConnected, simMode, refreshLatest]);

  if (isLoading) {
    return (
      <div className="app-container" style={{ justifyContent: 'center', alignItems: 'center' }}>
        <div className="text-center" style={{ padding: '80px 20px' }}>
          <p className="text-secondary">Loading stored readings…</p>
        </div>
      </div>
    );
  }

  const pageProps = {
    latestReading,
    history,
    health,
    isBackendConnected,
    dataSource,
    simMode,
    onModeChange: setSimMode,
    isSimRunning,
    onToggleSim: () => setIsSimRunning(v => !v),
    onSendSingle: handleSendSingle,
    onRefresh: refreshLatest,
  };

  const pages = {
    overview:   <DashboardPage {...pageProps} />,
    monitoring: <SensorMonitoringPage {...pageProps} />,
    detection:  <PredictionPage isBackendConnected={isBackendConnected} onRefresh={refreshLatest} />,
    history:    <HistoryPage isBackendConnected={isBackendConnected} />,
    alerts:     <AlertsPage isBackendConnected={isBackendConnected} />,
    help:       <HelpPage />,
  };

  return (
    <div className="app-container">
      <Header
        activeTab={activeTab}
        onTabChange={setActiveTab}
        health={health}
        isBackendConnected={isBackendConnected}
      />

      {!isBackendConnected && (
        <div className="main-content" style={{ paddingBottom: 0 }}>
          <div className="error-banner">
            <span className="error-banner-text">
              {loadError || 'Monitoring service is unreachable. Ensure the backend is running on port 5000.'}
            </span>
            <button className="btn btn-outline btn-sm" onClick={fetchData}>Retry</button>
          </div>
        </div>
      )}

      <main className="main-content">
        {pages[activeTab] || pages.overview}
      </main>

      <Footer />
    </div>
  );
}
