export const API_CONFIG = {
    BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000',
    CALLS_LIMIT: {
      DASHBOARD: 50000,    
      EXPORT: 100000,      
      PREVIEW: 1000,       
      MAX: 200000,        
    },
  };