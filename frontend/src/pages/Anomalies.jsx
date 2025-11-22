import React, { useState } from 'react';
import { useAnomalyData } from '../hooks/useAnomalyData';
import AnomalySummaryCards from '../components/anomalies/AnomalySummaryCards';
import AnomalyTimeline from '../components/anomalies/AnomalyTimeline';

const Anomalies = () => {
  const [severityFilter, setSeverityFilter] = useState(null);
  const { anomalies, loading, error } = useAnomalyData(100, severityFilter);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-gray-400">Loading anomaly data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-red-400">Error: {error}</div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-green-500">Anomaly Detection</h1>
        
        <div className="flex gap-2">
          <button
            onClick={() => setSeverityFilter(null)}
            className={`px-4 py-2 rounded ${
              severityFilter === null 
                ? 'bg-green-600 text-white' 
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`} >
            All
          </button>
          <button
            onClick={() => setSeverityFilter('High')}
            className={`px-4 py-2 rounded ${
              severityFilter === 'High' 
                ? 'bg-red-600 text-white' 
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`} >
            High
          </button>
          <button
            onClick={() => setSeverityFilter('Medium')}
            className={`px-4 py-2 rounded ${
              severityFilter === 'Medium' 
                ? 'bg-yellow-600 text-white' 
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`} >
            Medium
          </button>
        </div>
      </div>

      <AnomalySummaryCards anomalies={anomalies} />
      
      <div className="mb-6">
        <AnomalyTimeline anomalies={anomalies} />
      </div>

      <div className="mb-6">
        <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
          <h3 className="text-lg font-semibold text-white mb-2">About Anomaly Detection</h3>
          <p className="text-gray-400 text-sm">
            Using Isolation Forest algorithm to identify unusual patterns in emergency call data. 
            Analyzes daily volume, emergency type distribution, and temporal patterns. 
            Detected {anomalies.length} anomalous days representing abnormal call patterns.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Anomalies;