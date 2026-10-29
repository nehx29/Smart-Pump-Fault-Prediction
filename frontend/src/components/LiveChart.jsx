import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

export default function LiveChart({ data, title }) {
  if (!data || data.length === 0) {
    return (
      <div className="card">
        <div className="card-header">
          <div className="card-header-left">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
            </svg>
            <span>{title || 'Sensor History'}</span>
          </div>
        </div>
        <div className="card-body">
          <div className="empty-state">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
            </svg>
            <p>No historical data available</p>
          </div>
        </div>
      </div>
    );
  }

  const chartData = [...data].reverse().map(item => {
    const ts = item.timestamp || '';
    const timePart = ts.includes(' ') ? ts.split(' ')[1] : ts.split('T')[1]?.split('.')[0] || ts;
    return {
      time: timePart,
      pressure: item.pressure,
      current: item.current,
      vibration: item.vibration,
    };
  });

  return (
    <div className="card">
      <div className="card-header">
        <div className="card-header-left">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
          </svg>
          <span>{title || 'Sensor History'}</span>
        </div>
        <span className="text-xs text-muted">{chartData.length} readings</span>
      </div>
      <div className="card-body">
        <div className="chart-container">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 5, right: 15, left: -20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(51,65,85,0.6)" />
              <XAxis
                dataKey="time"
                stroke="#64748b"
                tick={{ fontSize: 10, fill: '#64748b' }}
                interval="preserveStartEnd"
              />
              <YAxis
                stroke="#64748b"
                tick={{ fontSize: 10, fill: '#64748b' }}
                domain={['auto', 'auto']}
              />
              <Tooltip
                contentStyle={{
                  background: '#334155',
                  border: '1px solid #475569',
                  borderRadius: 8,
                  fontSize: 12,
                  color: '#f1f5f9',
                }}
              />
              <Legend wrapperStyle={{ fontSize: 11, color: '#94a3b8' }} />
              <Line type="monotone" dataKey="pressure" name="Pressure (bar)" stroke="#06b6d4" strokeWidth={2} dot={false} activeDot={{ r: 4 }} />
              <Line type="monotone" dataKey="current" name="Current (A)" stroke="#f97316" strokeWidth={2} dot={false} activeDot={{ r: 4 }} />
              <Line type="monotone" dataKey="vibration" name="Vibration (mm/s)" stroke="#10b981" strokeWidth={2} dot={false} activeDot={{ r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
