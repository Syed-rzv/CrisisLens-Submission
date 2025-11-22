import React, { useState } from 'react';

const AnomalyTable = ({ anomalies }) => {
  const [sortField, setSortField] = useState('date');
  const [sortDir, setSortDir] = useState('desc');

  if (!anomalies || anomalies.length === 0) {
    return <div className="text-gray-400 text-center py-8">No anomalies to display</div>;
  }

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDir(sortDir === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDir('desc');
    }
  };

  const sorted = [...anomalies].sort((a, b) => {
    let aVal = a[sortField];
    let bVal = b[sortField];
    
    if (sortField === 'date') {
      aVal = new Date(aVal).getTime();
      bVal = new Date(bVal).getTime();
    }
    
    return sortDir === 'asc' ? aVal - bVal : bVal - aVal;
  });

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-900">
            <tr>
              {['Date', 'Calls', 'Severity', 'Reason'].map((header, idx) => {
                const field = header.toLowerCase().replace(' ', '_');
                const isActive = sortField === (field === 'calls' ? 'actual_calls' : field);
                
                return (
                  <th 
                    key={idx}
                    onClick={() => handleSort(field === 'calls' ? 'actual_calls' : field)}
                    className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider cursor-pointer hover:text-gray-200" >
                    {header} {isActive && (sortDir === 'asc' ? '↑' : '↓')}
                  </th>
                );
              })}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-700">
            {sorted.map((anomaly, idx) => (
              <tr key={idx} className="hover:bg-gray-750">
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                  {new Date(anomaly.date).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric'
                  })}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-white font-semibold">
                  {anomaly.actual_calls}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 py-1 text-xs font-semibold rounded ${
                    anomaly.severity === 'High' 
                      ? 'bg-red-900 text-red-200' 
                      : 'bg-yellow-900 text-yellow-200'
                  }`}>
                    {anomaly.severity}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-gray-400">
                  {anomaly.reason}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default AnomalyTable;