import React from 'react';
import { Clock, TrendingUp, Calendar } from 'lucide-react';
import { useTemporalData } from '../hooks/useTemporalData';
import PeakHoursHeatmap from '../components/temporal/PeakHoursHeatmap';
import SeasonalTrendsChart from '../components/temporal/SeasonalTrendsChart';
import TypePatternsChart from '../components/temporal/TypePatternsChart';
import ExpandableCard from '../components/common/ExpandableCard';

const TemporalAnalysis = () => {
  const {
    peakHours,
    seasonalTrends,
    typePatterns,
    summaryStats,
    loading,
    error
  } = useTemporalData();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-950">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-green-500 mx-auto mb-4"></div>
          <p className="text-green-500">Loading temporal analysis...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-950">
        <div className="text-center text-red-500">
          <p className="text-xl mb-2"> Error loading data</p>
          <p className="text-sm">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen bg-gray-950 p-3 overflow-hidden flex flex-col">
      <div className="max-w-[1900px] mx-auto w-full flex-1 flex flex-col min-h-0">
        <div className="text-center mb-2">
          <h1 className="text-xl font-bold text-green-500 mb-0.5">
            Temporal Analysis
          </h1>
          <p className="text-[10px] text-gray-400">
            Analyze emergency call patterns across time
          </p>
        </div>

        <div className="flex-1 flex flex-col gap-2 min-h-0">
          {/* Top Section: Heatmap + KPI Cards Side-by-Side */}
          <div className="h-[55%] flex gap-2">
            <div className="flex-1 bg-gray-900 rounded-lg p-3 border border-green-500/20">
              <h3 className="text-sm font-semibold text-white mb-2">
                Peak Hours Heatmap
              </h3>
              <div className="h-[calc(100%-28px)] overflow-auto">
                <PeakHoursHeatmap data={peakHours} />
              </div>
            </div>

            {/* KPI Cards */}
            {summaryStats && (
              <div className="w-48 flex flex-col gap-2">
                <div className="bg-gray-900 rounded-lg p-3 border border-green-500/20 flex-1 flex flex-col justify-center">
                  <div className="flex items-center gap-2 mb-1">
                    <Clock className="w-5 h-5 text-green-500 flex-shrink-0" />
                    <div className="text-[10px] text-gray-400">Busiest Hour</div>
                  </div>
                  <div className="text-2xl font-bold text-green-500 mb-1">
                    {summaryStats.busiest_hour.hour}:00
                  </div>
                  <div className="text-[9px] text-gray-500">
                    {summaryStats.busiest_hour.count} calls avg
                  </div>
                </div>

                <div className="bg-gray-900 rounded-lg p-3 border border-green-500/20 flex-1 flex flex-col justify-center">
                  <div className="flex items-center gap-2 mb-1">
                    <Calendar className="w-5 h-5 text-green-500 flex-shrink-0" />
                    <div className="text-[10px] text-gray-400">Busiest Day</div>
                  </div>
                  <div className="text-2xl font-bold text-green-500 mb-1">
                    {summaryStats.busiest_day.label}
                  </div>
                  <div className="text-[9px] text-gray-500">
                    {summaryStats.busiest_day.count} calls
                  </div>
                </div>

                <div className="bg-gray-900 rounded-lg p-3 border border-green-500/20 flex-1 flex flex-col justify-center">
                  <div className="flex items-center gap-2 mb-1">
                    <TrendingUp className="w-5 h-5 text-green-500 flex-shrink-0" />
                    <div className="text-[10px] text-gray-400">Avg Daily Calls</div>
                  </div>
                  <div className="text-2xl font-bold text-green-500 mb-1">
                    {summaryStats.average_daily_calls}
                  </div>
                  <div className="text-[9px] text-gray-500">
                    Historical data
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className="h-[45%] grid grid-cols-2 gap-2">
            <ExpandableCard title="Seasonal Trends" className="h-full">
              <SeasonalTrendsChart data={seasonalTrends} />
            </ExpandableCard>

            <ExpandableCard title="Type Patterns" className="h-full">
              <TypePatternsChart data={typePatterns} />
            </ExpandableCard>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TemporalAnalysis;