import React, { useState } from 'react';
import { Maximize2 } from 'lucide-react';
import VisualizationModal from './VisualizationModal';

const ExpandableCard = ({ title, children, className = '' }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <>
      <div 
        className={`bg-gray-900 border border-gray-800 rounded-lg p-3 cursor-pointer 
                    transition-all duration-200 hover:border-green-500/50 hover:shadow-lg 
                    hover:shadow-green-500/10 group ${className}`}
        onClick={() => setIsExpanded(true)} >
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-medium text-gray-100">{title}</h3>
          <Maximize2 
            size={16} 
            className="text-gray-500 group-hover:text-green-500 transition-colors" />
        </div>
        
        <div className="relative h-[calc(100%-32px)]">
          {React.cloneElement(children, { compact: true })}
          
          <div className="absolute inset-0 bg-gradient-to-t from-gray-900/50 to-transparent 
                          opacity-0 group-hover:opacity-100 transition-opacity 
                          pointer-events-none flex items-end justify-center pb-3">
            <span className="text-xs text-green-400 font-medium">
              Click to expand
            </span>
          </div>
        </div>
      </div>

      {isExpanded && (
        <VisualizationModal 
          title={title} 
          onClose={() => setIsExpanded(false)} >
          {React.cloneElement(children, { compact: false })}
        </VisualizationModal>
      )}
    </>
  );
};

export default ExpandableCard;