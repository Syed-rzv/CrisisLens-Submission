import { useState, useEffect } from 'react';
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

export const useTemporalData = () => {
  const [peakHours, setPeakHours] = useState(null);
  const [seasonalTrends, setSeasonalTrends] = useState(null);
  const [typePatterns, setTypePatterns] = useState(null);
  const [summaryStats, setSummaryStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchTemporalData = async (filters = {}) => {
    setLoading(true);
    setError(null);

    try {
      const queryParams = new URLSearchParams();
      
      if (filters.startDate) queryParams.append('start_date', filters.startDate);
      if (filters.endDate) queryParams.append('end_date', filters.endDate);
      if (filters.type) queryParams.append('type', filters.type);

      const endpoints = {
        peakHours: `${API_BASE_URL}/temporal/peak-hours?${queryParams}`,
        seasonalTrends: `${API_BASE_URL}/temporal/seasonal-trends?${queryParams}`,
        typePatterns: `${API_BASE_URL}/temporal/type-patterns`,
        summaryStats: `${API_BASE_URL}/temporal/summary-stats`
      };

      const [peakRes, seasonalRes, patternRes, statsRes] = await Promise.all([
        fetch(endpoints.peakHours),
        fetch(endpoints.seasonalTrends),
        fetch(endpoints.typePatterns),
        fetch(endpoints.summaryStats)
      ]);

      const [peakData, seasonalData, patternData, statsData] = await Promise.all([
        peakRes.json(),
        seasonalRes.json(),
        patternRes.json(),
        statsRes.json()
      ]);

      setPeakHours(peakData.data);
      setSeasonalTrends(seasonalData.data);
      setTypePatterns(patternData.data);
      setSummaryStats(statsData.data);
      
    } catch (err) {
      setError(err.message);
      console.error('Temporal data fetch failed:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTemporalData();
  }, []);

  return {
    peakHours,
    seasonalTrends,
    typePatterns,
    summaryStats,
    loading,
    error,
    refetch: fetchTemporalData
  };
};