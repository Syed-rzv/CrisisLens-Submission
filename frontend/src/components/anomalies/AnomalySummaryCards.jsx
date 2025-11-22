import React from 'react';
import { AlertTriangle, TrendingUp, Activity, BarChart3 } from 'lucide-react';

const AnomalySummaryCards = ({ anomalies }) => {
  if (!anomalies || anomalies.length === 0) {
    return (
      <div className="text-gray-400 text-center py-8">
        No anomalies detected
      </div>
    );
  }

  const totalAnomalies = anomalies.length;
  const highSeverity = anomalies.filter(a => a.severity === 'High').length;
  const avgCalls = Math.round(
    anomalies.reduce((sum, a) => sum + a.actual_calls, 0) / totalAnomalies
  );
  
  const topAnomaly = anomalies.reduce((max, a) => 
    a.actual_calls > max.actual_calls ? a : max
  );
  const topDate = new Date(topAnomaly.date).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  });

  const cards = [
    { 
      label: 'Total Anomalies', 
      value: totalAnomalies,
      icon: Activity,
      color: 'text-green-400',
      bgColor: 'bg-green-500/10' },
    { 
      label: 'High Severity', 
      value: highSeverity,
      icon: AlertTriangle,
      color: 'text-red-400',
      bgColor: 'bg-red-500/10' },
    { 
      label: 'Highest Spike', 
      value: `${topAnomaly.actual_calls} calls`, 
      sub: topDate,
      icon: TrendingUp,
      color: 'text-orange-400',
      bgColor: 'bg-orange-500/10'},
    { 
      label: 'Avg Anomaly Volume', 
      value: avgCalls,
      icon: BarChart3,
      color: 'text-blue-400',
      bgColor: 'bg-blue-500/10'}
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {cards.map((card, idx) => {
        const Icon = card.icon;
        return (
          <div 
            key={idx} 
            className="bg-gradient-to-br from-gray-800/80 to-gray-800/50 backdrop-blur-sm rounded-xl border border-gray-700/50 p-4 hover:border-gray-600/50 transition-all" >
            <div className="flex items-start justify-between mb-3">
              <div className="text-gray-400 text-xs font-medium uppercase tracking-wide">
                {card.label}
              </div>
              <div className={`p-2 rounded-lg ${card.bgColor}`}>
                <Icon className={`w-4 h-4 ${card.color}`} />
              </div>
            </div>
            <div className={`text-3xl font-bold ${card.color} mb-1`}>
              {card.value}
            </div>
            {card.sub && (
              <div className="text-gray-500 text-xs">
                {card.sub}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};

export default AnomalySummaryCards;