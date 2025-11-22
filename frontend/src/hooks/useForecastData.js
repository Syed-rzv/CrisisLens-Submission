import { useState, useEffect } from 'react';
import { API_CONFIG } from '../config/constants';

export const useForecastData = (emergencyType = 'Overall', days = null) => {
  const [forecasts, setForecasts] = useState([]);
  const [historical, setHistorical] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchForecasts = async () => {
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams({ type: emergencyType });
      if (days) params.append('days', days);

      const [forecastRes, summaryRes] = await Promise.all([
        fetch(`${API_CONFIG.BASE_URL}/forecasts?${params}`),
        fetch(`${API_CONFIG.BASE_URL}/forecast-summary?${params}`)
      ]);

      if (!forecastRes.ok || !summaryRes.ok) {
        throw new Error('Failed to fetch forecast data');
      }

      const forecastData = await forecastRes.json();
      const summaryData = await summaryRes.json();

      setForecasts(forecastData.forecasts || []);
      setHistorical(forecastData.historical || []);
      setSummary(summaryData.summary || null);
    } catch (err) {
      setError(err.message);
      console.error('Forecast data fetch failed:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchForecasts();
  }, [emergencyType, days]);

  return {
    forecasts,
    historical,
    summary,
    loading,
    error,
    refetch: fetchForecasts
  };
};