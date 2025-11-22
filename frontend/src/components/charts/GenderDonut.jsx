import React from 'react';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';
import CustomTooltip from '../common/CustomTooltip';

const COLORS = ['#3b82f6', '#ec4899'];

const GenderDonut = ({ data, hideTitle = false, compact = false }) => {
  const total = data.reduce((sum, item) => sum + item.count, 0);
  
  const renderLabel = (entry) => {
    const percent = ((entry.count / total) * 100).toFixed(1);
    return `${entry.gender}: ${percent}%`;
  };

  return (
    <div className="w-full h-full flex flex-col">
      {!hideTitle && !compact && (
        <div className="mb-4">
          <h3 className="text-lg font-semibold text-green-500">Gender Distribution</h3>
        </div>
      )}

      <div className="flex-1 min-h-0">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={70}
              outerRadius={100}
              paddingAngle={5}
              dataKey="count"
              label={renderLabel}
              labelLine={true} >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default GenderDonut;