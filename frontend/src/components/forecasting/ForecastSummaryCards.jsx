import React from 'react';
import { TrendingUp, Calendar, AlertCircle } from 'lucide-react';
import { useForecastData } from '../../hooks/useForecastData';

const ForecastSummaryCards = () => {
  const { summary, loading, error } = useForecastData('Overall', 7);

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        {[1, 2, 3].map(i => (
          <div key={i} className="bg-gray-900 rounded-lg p-6 border border-gray-800 animate-pulse">
            <div className="h-20"></div>
          </div>
        ))}
      </div> );
  }

  if (error || !summary) return null;

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <div className="bg-gray-900 rounded-lg p-6 border border-green-500/20 hover:border-green-500/40 transition-colors">
        <div className="flex items-center gap-3 mb-3">
          <TrendingUp className="w-8 h-8 text-green-500" />
          <div>
            <div className="text-sm text-gray-400">Avg Daily Forecast</div>
            <div className="text-2xl font-bold text-green-500">
              {summary.avg_predicted}
            </div>
          </div>
        </div>
        <div className="text-xs text-gray-500">
          Next 7 days average
        </div>
      </div>

      <div className="bg-gray-900 rounded-lg p-6 border border-orange-500/20 hover:border-orange-500/40 transition-colors">
        <div className="flex items-center gap-3 mb-3">
          <AlertCircle className="w-8 h-8 text-orange-500" />
          <div>
            <div className="text-sm text-gray-400">Peak Forecast</div>
            <div className="text-2xl font-bold text-orange-500">
              {summary.peak_calls}
            </div>
          </div>
        </div>
        <div className="text-xs text-gray-500">
          Expected on {new Date(summary.peak_day).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
        </div>
      </div>

      <div className="bg-gray-900 rounded-lg p-6 border border-blue-500/20 hover:border-blue-500/40 transition-colors">
        <div className="flex items-center gap-3 mb-3">
          <Calendar className="w-8 h-8 text-blue-500" />
          <div>
            <div className="text-sm text-gray-400">Forecast Period</div>
            <div className="text-2xl font-bold text-blue-500">
              {summary.total_days} days
            </div>
          </div>
        </div>
        <div className="text-xs text-gray-500">
          {new Date(summary.start_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - {new Date(summary.end_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
        </div>
      </div>
    </div>
  );
};

export default ForecastSummaryCards;