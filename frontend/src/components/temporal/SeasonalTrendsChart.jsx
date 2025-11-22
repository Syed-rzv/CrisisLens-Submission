import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const SeasonalTrendsChart = ({ data, compact = false }) => {
  if (!data || Object.keys(data).length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        No seasonal trends data available
      </div>
    );
  }

  const chartData = {};
  
  Object.entries(data).forEach(([type, trends]) => {
    trends.forEach(point => {
      const key = point.date;
      if (!chartData[key]) {
        chartData[key] = { date: key };
      }
      chartData[key][type] = point.count;
    });
  });

  const transformedData = Object.values(chartData).sort((a, b) => 
    a.date.localeCompare(b.date)
  );

  const colors = { 'EMS': '#22c55e', 'Fire': '#ef4444', 'Traffic': '#3b82f6' };

  const fontSize = compact ? 10 : 12;
  const showLegend = !compact;
  const chartHeight = compact ? 200 : 500;

  return (
    <div className="w-full h-full flex flex-col">
      {!compact && (
        <>
          <h3 className="text-xl font-semibold text-green-500 mb-2">
            📈 Seasonal Trends
          </h3>
          <p className="text-sm text-gray-400 mb-4">
            Monthly call volume patterns over time
          </p>
        </>
      )}

      <div style={{ width: '100%', height: chartHeight }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={transformedData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis 
              dataKey="date" 
              stroke="#9ca3af"
              tick={{ fill: '#9ca3af', fontSize }}
              interval={compact ? 'preserveStartEnd' : 'auto'}  />
            <YAxis 
              stroke="#9ca3af"
              tick={{ fill: '#9ca3af', fontSize }}  />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#1f2937', 
                border: '1px solid #22c55e',
                borderRadius: '8px',
                fontSize: '12px'
              }}
              labelStyle={{ color: '#22c55e' }} />
            {showLegend && (
              <Legend wrapperStyle={{ color: '#9ca3af' }} />
            )}
            {Object.keys(data).map(type => (
              <Line
                key={type}
                type="monotone"
                dataKey={type}
                stroke={colors[type] || '#22c55e'}
                strokeWidth={compact ? 1.5 : 2}
                dot={compact ? false : { r: 3 }}
                activeDot={{ r: compact ? 3 : 5 }} />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>

      {compact && (
        <div className="mt-2 grid grid-cols-3 gap-1">
          {Object.entries(data).map(([type, trends]) => {
            const totalCalls = trends.reduce((sum, t) => sum + t.count, 0);
            const avgMonthly = Math.round(totalCalls / trends.length);
            
            return (
              <div key={type} className="bg-gray-800 rounded-lg p-1.5 border border-green-500/10">
                <div className="text-[10px] text-gray-400">{type}</div>
                <div className="text-sm font-semibold text-green-500">
                  {avgMonthly}
                </div>
                <div className="text-[9px] text-gray-500">avg/month</div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default SeasonalTrendsChart;