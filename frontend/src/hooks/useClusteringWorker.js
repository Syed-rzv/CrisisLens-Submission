import { useState, useEffect, useRef, useMemo } from 'react';

export const useClusteringWorker = (data, params) => {
  const [clusters, setClusters] = useState([]);
  const [outliers, setOutliers] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [progress, setProgress] = useState(0);
  
  const workerRef = useRef(null);
  const cacheRef = useRef(new Map()); // Cache for memoization
  
  // Create cache key from data and params
  const cacheKey = useMemo(() => {
    return JSON.stringify({
      dataLength: data.length,
      dataHash: hashData(data), // hash of first/last items
      params
    });
  }, [data, params]);
  
  useEffect(() => {
    // Check cache first
    if (cacheRef.current.has(cacheKey)) {
      console.log('Using cached clustering results');
      const cached = cacheRef.current.get(cacheKey);
      setClusters(cached.clusters);
      setOutliers(cached.outliers);
      setIsLoading(false);
      return;
    }
    
    // Create worker if not exists
    if (!workerRef.current) {
      workerRef.current = new Worker(
        new URL('../workers/clustering.worker.js', import.meta.url),
        { type: 'module' }
      );
    }
    
    const worker = workerRef.current;
    
    setIsLoading(true);
    setError(null);
    setProgress(0);
    
    const progressInterval = setInterval(() => {
      setProgress(prev => Math.min(prev + 10, 90));
    }, 300);
    
    worker.onmessage = (e) => {
      clearInterval(progressInterval);
      setProgress(100);
      
      if (e.data.status === 'success') {
        setClusters(e.data.clusters);
        setOutliers(e.data.outliers);
        
        // Cache results
        cacheRef.current.set(cacheKey, {
          clusters: e.data.clusters,
          outliers: e.data.outliers
        });
        
        if (cacheRef.current.size > 10) {
          const firstKey = cacheRef.current.keys().next().value;
          cacheRef.current.delete(firstKey);
        }
        
        setIsLoading(false);
      } else {
        setError(e.data.error);
        setIsLoading(false);
      }
    };
    
    worker.onerror = (err) => {
      clearInterval(progressInterval);
      setError(err.message);
      setIsLoading(false);
    };
    
    // Send data to worker
    worker.postMessage({ data, params });
    
    // Cleanup
    return () => {
      clearInterval(progressInterval);
    };
  }, [data, params, cacheKey]);
  
  useEffect(() => {
    return () => {
      if (workerRef.current) {
        workerRef.current.terminate();
      }
    };
  }, []);
  
  return {
    clusters,
    outliers,
    isLoading,
    error,
    progress
  };
};

// hash function for cache key
function hashData(data) {
  if (data.length === 0) return '0';
  
  // Hash based on first, middle, last items
  const first = data[0];
  const middle = data[Math.floor(data.length / 2)];
  const last = data[data.length - 1];
  
  return `${first?.id || 0}-${middle?.id || 0}-${last?.id || 0}`;
}