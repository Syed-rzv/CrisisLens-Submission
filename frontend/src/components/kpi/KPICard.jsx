import React from 'react';

const KPICard = ({ icon: Icon, label, value, trend, gradient, compact = false }) => {
  if (compact) {
    return (
      <div className="bg-gray-900 border border-gray-800 rounded-lg p-2">
        <div className="flex items-center gap-2 mb-1">
          <Icon className="w-4 h-4 text-green-500 flex-shrink-0" />
          <span className="text-[10px] text-gray-400">{label}</span>
        </div>
        <div className="text-lg font-bold text-green-500">{value}</div>
        {trend && (
          <div className={`text-[9px] ${trend > 0 ? 'text-green-400' : 'text-red-400'}`}>
            {trend > 0 ? '+' : ''}{trend}%
          </div> )}
      </div>
    );
  }

  return (
    <div className={`${gradient} backdrop-blur-sm border border-green-500/20 rounded-xl p-6 hover:border-green-500/40 transition-all`}>
      <div className="flex items-center justify-between mb-4">
        <Icon className="w-8 h-8 text-green-500" />
        {trend && (
          <span className={`text-sm font-semibold ${trend > 0 ? 'text-green-400' : 'text-red-400'}`}>
            {trend > 0 ? '+' : ''}{trend}%
          </span> )}
      </div>
      <p className="text-sm text-gray-400 mb-1">{label}</p>
      <p className="text-3xl font-bold text-green-500">{value}</p>
    </div>
  );
};

export default KPICard;