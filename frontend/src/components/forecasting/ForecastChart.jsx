import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, ComposedChart } from 'recharts';
import { useForecastData } from '../../hooks/useForecastData';

const ForecastChart = ({ emergencyType = 'Overall' }) => {
  const { forecasts, historical, loading, error } = useForecastData(emergencyType);

  if (loading) {
    return (
      <div className="bg-gray-900 rounded-lg p-6 border border-green-500/20">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-800 rounded w-1/4 mb-4"></div>
          <div className="h-80 bg-gray-800 rounded"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-gray-900 rounded-lg p-6 border border-red-500/20">
        <p className="text-red-500">Failed to load forecast data: {error}</p>
      </div>
    );
  }

  if (!forecasts || forecasts.length === 0) {
    return (
      <div className="bg-gray-900 rounded-lg p-6 border border-gray-800">
        <p className="text-gray-500">No forecast data available</p>
      </div>
    );
  }

  const historicalChartData = (historical || []).map(h => ({
    date: new Date(h.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    actual: Math.round(h.actual_calls)
  }));

  const forecastChartData = forecasts.map(f => ({
    date: new Date(f.forecast_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    prediction: Math.round(f.predicted_calls),
    lower: Math.round(f.lower_bound),
    upper: Math.round(f.upper_bound)
  }));

  // Duplicated last historical point as first forecast point to connect lines
  const lastHistoricalPoint = historicalChartData.length > 0 
    ? historicalChartData[historicalChartData.length - 1] 
    : null;

  const firstForecastPoint = forecastChartData.length > 0 
    ? forecastChartData[0] 
    : null;

  const bridgePoint = lastHistoricalPoint && firstForecastPoint ? {
    date: lastHistoricalPoint.date,
    actual: lastHistoricalPoint.actual,
    prediction: lastHistoricalPoint.actual, // Start prediction at same point
    lower: undefined,
    upper: undefined
  } : null;

  // Combine data
  const chartData = bridgePoint
    ? [...historicalChartData, bridgePoint, ...forecastChartData]
    : [...historicalChartData, ...forecastChartData];

  return (
    <div className="bg-gray-900 rounded-lg p-6 border border-green-500/20">
      <div className="mb-4">
        <h3 className="text-xl font-semibold text-green-500">
          📈 Historical vs Forecast - {emergencyType}
        </h3>
        <p className="text-sm text-gray-400 mt-1">
          Last 30 days (actual) + Next 30 days (ARIMA predictions with 95% CI)
        </p>
      </div>

      <ResponsiveContainer width="100%" height={400}>
        <ComposedChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis 
            dataKey="date" 
            stroke="#9CA3AF"
            tick={{ fill: '#9CA3AF', fontSize: 12 }} />
          <YAxis 
            stroke="#9CA3AF"
            tick={{ fill: '#9CA3AF', fontSize: 12 }} />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: '#1F2937', 
              border: '1px solid #10B981',
              borderRadius: '8px'
            }}
            labelStyle={{ color: '#10B981' }} />
          <Legend 
            wrapperStyle={{ paddingTop: '20px' }}
            iconType="line" />
          
          {/* Historical actual calls */}
          <Line 
            type="monotone" 
            dataKey="actual" 
            stroke="#3B82F6" 
            strokeWidth={2}
            dot={{ fill: '#3B82F6', r: 3 }}
            name="Historical Calls" />
          
          {/* Confidence interval */}
          <Area 
            type="monotone"
            dataKey="upper"
            stroke="none"
            fill="#10B981"
            fillOpacity={0.1}
            name="Upper Bound" />

          <Area 
            type="monotone"
            dataKey="lower"
            stroke="none"
            fill="#10B981"
            fillOpacity={0.1}
            name="Lower Bound" />
          
          {/* Prediction line */}
          <Line 
            type="monotone" 
            dataKey="prediction" 
            stroke="#10B981" 
            strokeWidth={3}
            dot={{ fill: '#10B981', r: 4 }}
            activeDot={{ r: 6 }}
            name="Predicted Calls" />
        </ComposedChart>
      </ResponsiveContainer>

      <div className="mt-4 flex items-center gap-4 text-sm flex-wrap">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
          <span className="text-gray-400">Historical (Last 30 Days)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-green-500 rounded-full"></div>
          <span className="text-gray-400">Forecast (Next 30 Days - ARIMA 9.93% MAPE)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-green-500/20 rounded-full"></div>
          <span className="text-gray-400">95% Confidence Interval</span>
        </div>
      </div>
    </div>
  );
};

export default ForecastChart;