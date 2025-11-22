import React, { useEffect } from 'react';
import { X } from 'lucide-react';

const VisualizationModal = ({ title, children, onClose }) => {
  
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') onClose();
    };
    
    document.addEventListener('keydown', handleEscape);
    document.body.style.overflow = 'hidden';
    
    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [onClose]);

  return (
    <div 
      className="fixed inset-0 z-[1050] flex items-center justify-center p-4 bg-black/85 backdrop-blur-sm animate-fadeIn"
      onClick={onClose} >
      <div 
        className="bg-gray-900 rounded-xl border border-green-500/30 shadow-2xl w-full max-w-6xl flex flex-col animate-slideUp"
        style={{ height: '85vh' }}
        onClick={(e) => e.stopPropagation()} >
        <div className="flex items-center justify-between p-4 border-b border-gray-800 bg-gray-900 z-10 flex-shrink-0">
          <h2 className="text-xl font-semibold text-white">{title}</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors p-2 hover:bg-gray-800 rounded-lg" >
            <X size={24} />
          </button>
        </div>
        
        <div className="flex-1 p-6 relative" style={{ overflow: 'visible' }}>
          {React.cloneElement(children, { compact: false })}
        </div>
      </div>
    </div>
  );
};

export default VisualizationModal;