import React, { useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import CustomTooltip from '../common/CustomTooltip';

const TimelineChart = ({ data, aggregatedData, onDataPointClick, compact = false, hideTitle = false }) => {
  const chartData = useMemo(() => {
    return aggregatedData || data;
  }, [aggregatedData, data]);

  const handleClick = (e) => {
    if (e && e.activeLabel && onDataPointClick) {
      onDataPointClick(e.activeLabel);
    }
  };

  return (
    <div className="w-full h-full flex flex-col">
      {!hideTitle && !compact && (
        <div className="mb-4">
          <h3 className="text-lg font-semibold text-green-500">Call Volume Over Time</h3>
        </div>
      )}
      
      <div className="flex-1 min-h-0">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} onClick={handleClick}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
            <XAxis 
              dataKey="month" 
              stroke="#9ca3af" 
              tick={{ fill: '#9ca3af' }}
              tickCount={20}
              minTickGap={30} />
            <YAxis 
              stroke="#9ca3af" 
              tick={{ fill: '#9ca3af' }}/>
            <Tooltip content={<CustomTooltip chartType="timeline" />} />
            
            <Line
              type="monotone"
              dataKey="count"
              stroke="#22c55e"
              strokeWidth={3}
              dot={{ fill: '#22c55e', r: 4 }}
              activeDot={{ r: 6 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default TimelineChart;