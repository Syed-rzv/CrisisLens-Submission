import React from 'react';

const PeakHoursHeatmap = ({ data }) => {
  if (!data || Object.keys(data).length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-gray-500">
        No peak hours data available
      </div>
    );
  }

  const dayNames = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  const hours = Array.from({ length: 24 }, (_, i) => i);
  
  let maxCount = 0;
  Object.values(data).forEach(dayData => {
    Object.values(dayData).forEach(count => {
      if (count > maxCount) maxCount = count;
    });
  });

  const getColor = (count) => {
    if (count === 0) return 'bg-gray-800';
    const intensity = count / maxCount;
    if (intensity > 0.8) return 'bg-red-600';
    if (intensity > 0.6) return 'bg-orange-500';
    if (intensity > 0.4) return 'bg-yellow-500';
    if (intensity > 0.2) return 'bg-green-500';
    return 'bg-blue-500';
  };

  return (
    <div className="flex flex-col items-center justify-center h-full py-2">
      <div className="inline-flex flex-col">
        <div className="flex mb-1">
          <div className="w-7 h-7"></div>
          <div className="flex gap-px">
            {hours.map(hour => (
              <div key={hour} className="w-7 h-7 text-center text-[9px] text-white font-bold flex items-center justify-center">
                {hour}
              </div>
            ))}
          </div>
        </div>

        <div className="space-y-px">
          {[1, 2, 3, 4, 5, 6, 7].map(day => {
            const dayData = data[day] || {};
            
            return (
              <div key={day} className="flex items-center">
                <div className="w-7 h-7 text-[9px] text-gray-400 font-bold flex items-center justify-end pr-1">
                  {dayNames[day - 1][0]}
                </div>
                <div className="flex gap-px">
                  {hours.map(hour => {
                    const count = dayData[hour] || 0;
                    
                    return (
                      <div key={`${day}-${hour}`}
                        className={`w-7 h-7 rounded ${getColor(count)} 
                                   hover:ring-2 hover:ring-green-500 transition-all
                                   cursor-pointer group relative`}
                        title={`${dayNames[day - 1]} ${hour}:00 - ${count} calls`} >
                        <span className="opacity-0 group-hover:opacity-100 
                                       absolute -top-7 left-1/2 transform -translate-x-1/2
                                       bg-gray-800 text-white text-[10px] px-2 py-0.5 rounded
                                       whitespace-nowrap z-10 pointer-events-none">
                          {count}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="mt-3 flex items-center justify-center gap-2">
        <span className="text-[9px] text-gray-400">Less</span>
        <div className="flex gap-0.5">
          <div className="w-4 h-4 bg-gray-800 rounded"></div>
          <div className="w-4 h-4 bg-blue-500 rounded"></div>
          <div className="w-4 h-4 bg-green-500 rounded"></div>
          <div className="w-4 h-4 bg-yellow-500 rounded"></div>
          <div className="w-4 h-4 bg-orange-500 rounded"></div>
          <div className="w-4 h-4 bg-red-600 rounded"></div>
        </div>
        <span className="text-[9px] text-gray-400">More</span>
      </div>
    </div>
  );
};

export default PeakHoursHeatmap;