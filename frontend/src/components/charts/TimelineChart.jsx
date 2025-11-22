import React, { useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceDot } from 'recharts';
import CustomTooltip from '../common/CustomTooltip';
import { detectTimelineAnomalies } from '../../utils/dataProcessing';

const TimelineChart = ({ data, onDataPointClick, compact = false, hideTitle = false }) => {
  const enrichedData = useMemo(() => {
    return detectTimelineAnomalies(data);
  }, [data]);

  const anomalyPoints = useMemo(() => {
    return enrichedData.filter(item => item.isAnomaly);
  }, [enrichedData]);

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

      {/* Anomaly alert */}
      {anomalyPoints.length > 0 && (
        <div className="mb-3 px-4 py-2 bg-red-500/10 border border-red-500/30 rounded-lg inline-block">
          <span className="text-red-400 text-sm font-semibold">
            ⚠️ {anomalyPoints.length} anomal{anomalyPoints.length === 1 ? 'y' : 'ies'} detected
          </span>
        </div>
      )}
      
      <div className="flex-1 min-h-0">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={enrichedData} onClick={handleClick}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
            <XAxis 
              dataKey="month" 
              stroke="#9ca3af" 
              tick={{ fill: '#9ca3af' }} />
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

            {anomalyPoints.map((point, idx) => (
              <ReferenceDot
                key={`anomaly-${idx}`}
                x={point.month}
                y={point.count}
                r={8}
                fill="#ef4444"
                stroke="#dc2626"
                strokeWidth={2}
                opacity={0.8} />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default TimelineChart;