import { useState, useEffect } from 'react';
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

export const useAnomalyData = (limit = 100, severity = null) => {
  const [anomalies, setAnomalies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAnomalies = async () => {
      try {
        setLoading(true);
        let url = `${API_BASE_URL}/anomalies?limit=${limit}`;
        if (severity) url += `&severity=${severity}`;
        
        const res = await fetch(url);
        if (!res.ok) throw new Error('Failed to fetch anomalies');
        
        const data = await res.json();
        setAnomalies(data);
        setError(null);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchAnomalies();
  }, [limit, severity]);

  return { anomalies, loading, error };
};