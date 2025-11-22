import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const TypePatternsChart = ({ data, compact = false }) => {
  if (!data || Object.keys(data).length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        No type patterns data available
      </div>
    );
  }

  const colors = { 'EMS': '#22c55e', 'Fire': '#ef4444', 'Traffic': '#3b82f6' };

  const hours = Array.from({ length: 24 }, (_, i) => i);
  const chartData = hours.map(hour => {
    const point = { hour: compact ? `${hour}` : `${hour}:00` };
    Object.entries(data).forEach(([type, patterns]) => {
      const hourData = patterns.find(p => p.hour === hour);
      point[type] = hourData ? hourData.count : 0;
    });
    return point;
  });

  const fontSize = compact ? 10 : 12;
  const showLegend = !compact;
  const chartHeight = compact ? 200 : 500;

  return (
    <div className="w-full h-full flex flex-col">
      {!compact && (
        <>
          <h3 className="text-xl font-semibold text-green-500 mb-2">
            📊 Type Patterns
          </h3>
          <p className="text-sm text-gray-400 mb-4">
            Hourly distribution by emergency type
          </p>
        </>
      )}

      <div style={{ width: '100%', height: chartHeight }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis 
              dataKey="hour" 
              stroke="#9ca3af"
              tick={{ fill: '#9ca3af', fontSize }}
              interval={compact ? 3 : 1}
            />
            <YAxis 
              stroke="#9ca3af"
              tick={{ fill: '#9ca3af', fontSize }}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#1f2937', 
                border: '1px solid #22c55e',
                borderRadius: '8px',
                fontSize: '12px'
              }}
              labelStyle={{ color: '#22c55e' }}
            />
            {showLegend && (
              <Legend wrapperStyle={{ color: '#9ca3af' }} />
            )}
            {Object.keys(data).map(type => (
              <Bar
                key={type}
                dataKey={type}
                fill={colors[type] || '#22c55e'}
                radius={compact ? [2, 2, 0, 0] : [4, 4, 0, 0]}
              />
            ))}
          </BarChart>
        </ResponsiveContainer>
      </div>

      {compact && (
        <div className="mt-2 grid grid-cols-3 gap-1">
          {Object.entries(data).map(([type, patterns]) => {
            const peakHour = patterns.reduce((max, p) => 
              p.count > max.count ? p : max, patterns[0]
            );
            
            return (
              <div key={type} className="bg-gray-800 rounded-lg p-1.5 border border-green-500/10">
                <div className="text-[10px] text-gray-400">{type} Peak</div>
                <div className="text-sm font-semibold" style={{ color: colors[type] }}>
                  {peakHour.hour}:00
                </div>
                <div className="text-[9px] text-gray-500">{peakHour.count} calls</div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default TypePatternsChart;