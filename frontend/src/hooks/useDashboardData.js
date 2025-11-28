import { useState, useEffect, useCallback } from 'react';
import api, { processApiData } from '../services/api';
import { generateMockData } from '../data/mockData';
import { API_CONFIG } from '../config/constants';

const useDashboardData = (filters = {}) => {
  const [data, setData] = useState([]);
  const [timelineData, setTimelineData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [usingMockData, setUsingMockData] = useState(false);
  const [apiAvailable, setApiAvailable] = useState(true);

  useEffect(() => {
    const initialize = async () => {
      const health = await api.healthCheck();
      setApiAvailable(health.available);
      
      if (!health.available) {
        console.warn('API unavailable, using mock data as fallback');
      }
      fetchData();
    };

    initialize();
  }, []);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      if (!apiAvailable) {
        console.log('Using mock data (API unavailable)');
        const mockData = generateMockData();
        setData(mockData);
        setUsingMockData(true);
        setLoading(false);
        return;
      }

      const [callsResponse, timelineResponse] = await Promise.all([
        api.getCalls({
          limit: API_CONFIG.CALLS_LIMIT.DASHBOARD, 
          ...filters,
        }),
        api.getTimelineAggregated(filters),
      ]);

      const transformedData = processApiData.transformCallsData(callsResponse);
      const transformedTimeline = processApiData.transformTimelineAggregated(timelineResponse);
      
      if (transformedData.length === 0) {
        console.warn('No data returned from API, using mock data');
        const mockData = generateMockData();
        setData(mockData);
        setUsingMockData(true);
      } else {
        setData(transformedData);
        setTimelineData(transformedTimeline);
        setUsingMockData(false);
      }
    } catch (err) {
      console.error('Error fetching data from API:', err);
      console.log('Falling back to mock data');
      
      const mockData = generateMockData();
      setData(mockData);
      setUsingMockData(true);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [apiAvailable, filters]);

  return {
    data,
    timelineData,
    loading,
    error,
    usingMockData,
    apiAvailable,
    refetch: fetchData,
  };
};

export const useStatsData = () => {
  const [stats, setStats] = useState({
    typeCounts: [],
    dailyStats: [],
    districtCounts: [],
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      setLoading(true);
      try {
        const [typeCounts, dailyStats, districtCounts] = await Promise.all([
          api.getTypeCounts(),
          api.getDailyStats(),
          api.getDistrictCounts(),
        ]);

        setStats({
          typeCounts: processApiData.transformTypeCounts(typeCounts),
          dailyStats: processApiData.transformDailyStats(dailyStats),
          districtCounts: processApiData.transformDistrictCounts(districtCounts),
        });
      } catch (err) {
        console.error('Error fetching stats:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  return { stats, loading, error };
};

export const useForecastData = (params = {}) => {
  const [forecast, setForecast] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchForecast = async () => {
      setLoading(true);
      try {
        const response = await api.getForecast(params);
        setForecast(processApiData.transformForecastData(response));
      } catch (err) {
        console.error('Error fetching forecast:', err);
        setError(err.message);
        setForecast([]);
      } finally {
        setLoading(false);
      }
    };

    fetchForecast();
  }, [JSON.stringify(params)]);

  return { forecast, loading, error };
};

export const useSubmitCall = () => {
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState(null);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  const submitCall = async (callData) => {
    setSubmitting(true);
    setSubmitError(null);
    setSubmitSuccess(false);

    try {
      const response = await api.ingestCall(callData);
      setSubmitSuccess(true);
      return response;
    } catch (err) {
      console.error('Error submitting call:', err);
      setSubmitError(err.message);
      throw err;
    } finally {
      setSubmitting(false);
    }
  };

  return {
    submitCall,
    submitting,
    submitError,
    submitSuccess,
  };
};

export default useDashboardData;