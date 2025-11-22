import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Scatter } from 'recharts';

const AnomalyTimeline = ({ anomalies }) => {
  if (!anomalies || anomalies.length === 0) {
    return <div className="text-gray-400 text-center py-8">No data available</div>;
  }

  // Sort by date
  const sorted = [...anomalies].sort((a, b) => 
    new Date(a.date) - new Date(b.date)
  );

  // Format data for chart
  const chartData = sorted.map(a => {
    const dateObj = new Date(a.date);
    return {
      date: dateObj.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric',
        year: '2-digit'
      }).replace(',', ''),
      calls: a.actual_calls,
      fullDate: a.date,
      severity: a.severity,
      reason: a.reason
    };
  });

  const CustomTooltip = ({ active, payload }) => {
    if (!active || !payload || !payload[0]) return null;
    
    const data = payload[0].payload;
    const fullDateFormatted = new Date(data.fullDate).toLocaleDateString('en-US', { 
      month: 'long', 
      day: 'numeric', 
      year: 'numeric' 
    });
    
    return (
      <div className="bg-gray-900 border border-gray-700 p-3 rounded shadow-lg">
        <p className="text-white font-semibold mb-1">{fullDateFormatted}</p>
        <p className="text-green-400">{data.calls} calls</p>
        <p className={`text-sm ${data.severity === 'High' ? 'text-red-400' : 'text-yellow-400'}`}>
          {data.severity} severity
        </p>
        <p className="text-gray-400 text-xs mt-2">{data.reason}</p>
      </div>
    );
  };

  return (
    <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
      <h3 className="text-xl font-semibold text-white mb-4">Anomaly Timeline</h3>
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis 
            dataKey="date" 
            stroke="#9CA3AF"
            tick={{ fill: '#9CA3AF', fontSize: 12 }}
            angle={-45}
            textAnchor="end"
            height={80} />
          <YAxis 
            stroke="#9CA3AF"
            tick={{ fill: '#9CA3AF' }}
            label={{ value: 'Call Volume', angle: -90, position: 'insideLeft', fill: '#9CA3AF' }} />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          <Line 
            type="monotone" 
            dataKey="calls" 
            stroke="#10B981" 
            strokeWidth={2}
            dot={{ fill: '#10B981', r: 4 }}
            name="Anomalous Days" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default AnomalyTimeline;