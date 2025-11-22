import React, { useState } from 'react';
import { TrendingUp } from 'lucide-react';
import ForecastChart from '../components/forecasting/ForecastChart';
import { useForecastData } from '../hooks/useForecastData';

const Forecasting = () => {
  const [selectedType, setSelectedType] = useState('Overall');
  const { summary } = useForecastData(selectedType);

  const emergencyTypes = ['Overall', 'EMS', 'Fire', 'Traffic'];

  return (
    <div className="min-h-screen bg-black p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6">
          <div className="flex items-center gap-3 mb-2">
            <TrendingUp className="w-10 h-10 text-green-500" />
            <h1 className="text-4xl font-bold text-green-500">Forecasting</h1>
          </div>
          <p className="text-gray-400">
            30-day call volume predictions using SARIMA statistical modeling
          </p>
        </div>

        {/* Emergency Type */}
        <div className="bg-gray-900 rounded-lg p-4 border border-green-500/20 mb-6">
          <div className="flex gap-3">
            {emergencyTypes.map(type => (
              <button
                key={type}
                onClick={() => setSelectedType(type)}
                className={`px-4 py-2 rounded-lg transition-all ${
                  selectedType === type
                    ? 'bg-green-500 text-black font-semibold'
                    : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                }`}
              >
                {type}
              </button>
            ))}
          </div>
        </div>

        {/* Summary Stats */}
        {summary && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-gray-900 rounded-lg p-4 border border-green-500/20">
              <div className="text-sm text-gray-400">Avg Forecast</div>
              <div className="text-2xl font-bold text-green-500">
                {summary.avg_predicted}
              </div>
              <div className="text-xs text-gray-500">calls/day</div>
            </div>

            <div className="bg-gray-900 rounded-lg p-4 border border-orange-500/20">
              <div className="text-sm text-gray-400">Peak Day</div>
              <div className="text-2xl font-bold text-orange-500">
                {summary.peak_calls}
              </div>
              <div className="text-xs text-gray-500">
                {new Date(summary.peak_day).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
              </div>
            </div>

            <div className="bg-gray-900 rounded-lg p-4 border border-blue-500/20">
              <div className="text-sm text-gray-400">Min Forecast</div>
              <div className="text-2xl font-bold text-blue-500">
                {summary.min_predicted}
              </div>
              <div className="text-xs text-gray-500">calls/day</div>
            </div>

            <div className="bg-gray-900 rounded-lg p-4 border border-purple-500/20">
              <div className="text-sm text-gray-400">Max Forecast</div>
              <div className="text-2xl font-bold text-purple-500">
                {summary.max_predicted}
              </div>
              <div className="text-xs text-gray-500">calls/day</div>
            </div>
          </div>
        )}

        {/* Forecast Chart */}
        <ForecastChart emergencyType={selectedType} />

        {/* Model Info */}
        <div className="mt-6 bg-gray-900 rounded-lg p-6 border border-green-500/20">
          <h3 className="text-lg font-semibold text-green-500 mb-3">
            About the Forecast Model
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-gray-400 mb-2">
                <span className="text-green-500 font-semibold">Model:</span> ARIMA (AutoRegressive Integrated Moving Average)
              </p>
              <p className="text-gray-400 mb-2">
                <span className="text-green-500 font-semibold">Accuracy:</span> 9.93% MAPE (Mean Absolute Percentage Error)
              </p>
              <p className="text-gray-400">
                <span className="text-green-500 font-semibold">Training Data:</span> 663,522 emergency calls over 5.6 years
              </p>
            </div>
            <div>
              <p className="text-gray-400 mb-2">
                <span className="text-green-500 font-semibold">Forecast Horizon:</span> 30 days ahead
              </p>
              <p className="text-gray-400 mb-2">
                <span className="text-green-500 font-semibold">Confidence Level:</span> 95% prediction intervals
              </p>
              <p className="text-gray-400">
                <span className="text-green-500 font-semibold">Update Frequency:</span> Generated from historical data (Aug 2020)
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Forecasting;