import React, { createContext, useContext, useState, useCallback } from 'react';

const FilterContext = createContext();

export const useFilters = () => useContext(FilterContext);

export const FilterProvider = ({ children }) => {
  const [filters, setFilters] = useState({
    dateRange: {
      start: '2000-01-01',
      end: '2030-12-31'
    },
    types: ['EMS', 'Fire', 'Traffic'],
    district: ''
  });

  const setDynamicDateRange = useCallback((data) => {
    if (!data || data.length === 0) return;
    
    const dates = data.map(item => new Date(item.timestamp));
    const minDate = new Date(Math.min(...dates));
    const maxDate = new Date(Math.max(...dates));
    
    setFilters(prev => ({
      ...prev,
      dateRange: {
        start: minDate.toISOString().split('T')[0],
        end: maxDate.toISOString().split('T')[0]
      }
    }));
  }, []);

  return (
    <FilterContext.Provider value={{ 
      filters, 
      setFilters, 
      setDynamicDateRange
    }}>
      {children}
    </FilterContext.Provider>
  );
};