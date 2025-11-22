import { useState, useEffect, useRef } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

export const useClusterData = (timeRange = 'all', minSeverity = null, dashboardFilters = null) => {
  const [clusters, setClusters] = useState([]);
  const [outliers, setOutliers] = useState([]);
  const [temporalAnalysis, setTemporalAnalysis] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const isMounted = useRef(true);
  const initialLoadDone = useRef(false);
  const abortController = useRef(null);

  useEffect(() => {
    return () => {
      isMounted.current = false;
      if (abortController.current) {
        abortController.current.abort();
      }
    };
  }, []);

  useEffect(() => {
    if (!initialLoadDone.current && timeRange !== 'all') {
      console.log('Waiting for initial clusters to load...');
      return;
    }

    if (abortController.current) {
      abortController.current.abort();
    }
    abortController.current = new AbortController();
    
    let timeoutId;
    
    const fetchClusters = async () => {
      if (!isMounted.current) return;
      
      setLoading(true);
      setError(null);

      try {
        const params = new URLSearchParams();
        if (timeRange !== 'all') params.append('time_range', timeRange);
        if (minSeverity) params.append('min_severity', minSeverity);

        if (dashboardFilters) {
          if (dashboardFilters.types && dashboardFilters.types.length > 0) {
            params.append('emergency_types', dashboardFilters.types.join(','));
          }
          if (dashboardFilters.dateRange) {
            params.append('start_date', dashboardFilters.dateRange.start);
            params.append('end_date', dashboardFilters.dateRange.end);
          }
          if (dashboardFilters.district) {
            params.append('district', dashboardFilters.district);
          }
        }

        const response = await fetch(
          `${API_BASE_URL}/clusters?${params.toString()}`,
          { signal: abortController.current.signal }
        );

        if (!response.ok) {
          throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();
        
        if (isMounted.current) {
          setClusters(data.clusters || []);
          setOutliers(data.outliers || []);
          setTemporalAnalysis(data.temporal_analysis || []);
          setSummary(data.summary || null);
          initialLoadDone.current = true;
        }
      } catch (err) {
        if (err.name === 'AbortError') {
          console.log('Request cancelled');
          return;
        }
        if (isMounted.current) {
          setError(err.message);
          console.error('Cluster data fetch error:', err);
        }
      } finally {
        if (isMounted.current) {
          setLoading(false);
        }
      }
    };

    timeoutId = setTimeout(() => {
      fetchClusters();
    }, 500);

    return () => {
      clearTimeout(timeoutId);
    };
  }, [timeRange, minSeverity, dashboardFilters]);

  return { clusters, outliers, temporalAnalysis, summary, loading, error };
};

export const useHeatmapData = (dashboardFilters = null) => {
  const [heatmapData, setHeatmapData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const isMounted = useRef(true);

  useEffect(() => {
    return () => {
      isMounted.current = false;
    };
  }, []);

  useEffect(() => {
    const fetchHeatmap = async () => {
      if (!isMounted.current) return;
      
      setLoading(true);
      setError(null);

      try {
        const params = new URLSearchParams();
        
        if (dashboardFilters) {
          if (dashboardFilters.types && dashboardFilters.types.length > 0) {
            params.append('emergency_types', dashboardFilters.types.join(','));
          }
          if (dashboardFilters.dateRange) {
            params.append('start_date', dashboardFilters.dateRange.start);
            params.append('end_date', dashboardFilters.dateRange.end);
          }
          if (dashboardFilters.district) {
            params.append('district', dashboardFilters.district);
          }
        }

        const response = await fetch(`${API_BASE_URL}/clusters/heatmap-data?${params.toString()}`);
        
        if (!response.ok) {
          throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();
        
        if (isMounted.current) {
          setHeatmapData(data.data || []);
        }
      } catch (err) {
        if (isMounted.current) {
          setError(err.message);
          console.error('Heatmap data fetch error:', err);
        }
      } finally {
        if (isMounted.current) {
          setLoading(false);
        }
      }
    };

    fetchHeatmap();
  }, [dashboardFilters]);

  return { heatmapData, loading, error };
};