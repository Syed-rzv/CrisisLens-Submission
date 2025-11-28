import React, { useState, useMemo } from 'react';
import { Phone, Activity, Clock, Users, Maximize2, Calendar, ChevronDown } from 'lucide-react';
import { useFilters } from '../context/FilterContext';
import useDashboardData from '../hooks/useDashboardData';
import Sidebar from './layout/Sidebar';
import TimelineChart from './charts/TimelineChart';
import TypePieChart from './charts/TypePieChart';
import AgeHistogram from './charts/AgeHistogram';
import GenderDonut from './charts/GenderDonut';
import MapView from './charts/MapView';
import Modal from './shared/Modal';
import DataTable from './shared/DataTable';
import SubmitCall from '../pages/SubmitCall';
import TemporalAnalysis from '../pages/TemporalAnalysis';
import Forecasting from '../pages/Forecasting';
import Anomalies from '../pages/Anomalies';
import UploadDataset from '../pages/UploadDataset';
import About from '../pages/About';
import { 
  filterData, 
  calculateKPIs, 
  aggregateTimelineData, 
  aggregateTypeData, 
  aggregateAgeData, 
  aggregateGenderData
} from '../utils/dataProcessing';
import AnimatedBackground from './layout/AnimatedBackground';

const Dashboard = () => {
  const [activeView, setActiveView] = useState('dashboard');
  const [expandedChart, setExpandedChart] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [modalData, setModalData] = useState({ title: '', data: [], columns: [] });
  const { data: rawData, timelineData: aggregatedTimelineData, loading } = useDashboardData();
  const { filters, setFilters } = useFilters();

  const filteredData = useMemo(() => {
    if (!rawData || rawData.length === 0) return [];
    return filterData(rawData, filters);
  }, [rawData, filters]);

  const kpis = useMemo(() => calculateKPIs(filteredData), [filteredData]);
  const timelineData = useMemo(() => { return aggregatedTimelineData && aggregatedTimelineData.length > 0 ? aggregatedTimelineData 
      : aggregateTimelineData(filteredData);}, [aggregatedTimelineData, filteredData]);

  const typeData = useMemo(() => {
    const data = aggregateTypeData(filteredData);
    const total = data.reduce((sum, d) => sum + d.count, 0);
    return data.map(d => ({
      ...d,
      percentage: total > 0 ? Math.round((d.count / total) * 100) : 0
    }));
  }, [filteredData]);
  
  const ageData = useMemo(() => aggregateAgeData(filteredData), [filteredData]);
  
  const genderData = useMemo(() => {
    const data = aggregateGenderData(filteredData);
    const total = data.reduce((sum, d) => sum + d.count, 0);
    return data.map(d => ({
      ...d,
      percentage: total > 0 ? Math.round((d.count / total) * 100) : 0
    }));
  }, [filteredData]);

  const heatmapPoints = useMemo(() => {
    return filteredData.map(item => ({
      lat: item.lat,
      lng: item.lng,
      intensity: 1
    }));
  }, [filteredData]);

  // Filter toggle handler
  const handleTypeToggle = (type) => {
    setFilters(prev => {
      const currentTypes = prev.types || [];
      const newTypes = currentTypes.includes(type)
        ? currentTypes.filter(t => t !== type)
        : [...currentTypes, type];
      return { ...prev, types: newTypes };
    });
  };

  // Drill-down table handler
  const showDataTable = (title, data) => {
    setModalData({ 
      title, 
      data,
      columns: [
        { field: 'timestamp', label: 'Date', format: (val) => new Date(val).toLocaleDateString() },
        { field: 'emergencyType', label: 'Type' },
        { field: 'district', label: 'Location' },
        { field: 'callerAge', label: 'Age' },
        { field: 'callerGender', label: 'Gender' }
      ]
    });
    setModalOpen(true);
  };

  if (activeView !== 'dashboard') {
    const pageComponents = {
      submit: SubmitCall,
      temporal: TemporalAnalysis,
      forecasting: Forecasting,
      anomalies: Anomalies,
      upload: UploadDataset,
      about: About
    };
    
    const PageComponent = pageComponents[activeView];
    
    return (
      <div className="min-h-screen bg-gray-950">
        <AnimatedBackground />
        <Sidebar activeView={activeView} setActiveView={setActiveView} />
        <div style={{ marginLeft: '256px', minHeight: '100vh' }}>
          {PageComponent && <PageComponent />}
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex h-screen bg-gray-950">
        <Sidebar activeView={activeView} setActiveView={setActiveView} />
        <div className="flex-1 flex items-center justify-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-green-500"></div>
        </div>
      </div>
    );
  }

  const CompactKPI = ({ icon: Icon, label, value, onClick }) => (
    <div 
      className={`bg-gray-900/60 backdrop-blur-sm rounded-xl border border-gray-800/50 p-4 hover:border-green-500/30 transition-all ${onClick ? 'cursor-pointer' : ''}`}
      onClick={onClick} >
      <div className="flex items-center gap-3">
        <div className="p-2 rounded-lg bg-green-500/10">
          <Icon size={18} className="text-green-500" />
        </div>
        <div className="flex flex-col">
          <span className="text-xs text-gray-500 uppercase tracking-wide">{label}</span>
          <span className="text-lg font-bold text-white">{value}</span>
        </div>
      </div>
    </div>
  );

  const CompactTypePreview = () => {
    const topType = typeData[0] || { type: 'N/A', percentage: 0, count: 0 };
    
    return (
      <div className="h-full flex flex-col items-center justify-center space-y-4">
        <div className="text-center">
          <div className="text-5xl font-bold text-white mb-2">{topType.percentage}%</div>
          <div className="text-sm text-gray-400">Most Common Type</div>
          <div className="text-lg font-semibold text-green-400 mt-1">{topType.type}</div>
        </div>
        
        <div className="w-full max-w-[200px]">
          <div className="flex gap-1 h-2 rounded-full overflow-hidden bg-gray-800">
            {typeData.map((type, i) => (
              <div
                key={i}
                style={{ width: `${type.percentage}%` }}
                className={`${
                  type.type === 'EMS' ? 'bg-green-500' :
                  type.type === 'Fire' ? 'bg-red-500' :
                  'bg-blue-500'
                }`} />
            ))}
          </div>
          <div className="flex justify-between mt-2 text-[10px] text-gray-500">
            {typeData.map((type, i) => (
              <span key={i}>{type.type} {type.percentage}%</span>
            ))}
          </div>
        </div>
      </div>
    );
  };

  const CompactAgePreview = () => {
    const peak = ageData.reduce((max, d) => d.count > max.count ? d : max, ageData[0]);
    const maxCount = Math.max(...ageData.map(d => d.count));
    
    return (
      <div className="h-full flex flex-col items-center justify-center space-y-4">
        <div className="text-center">
          <div className="text-5xl font-bold text-white mb-2">{peak.range}</div>
          <div className="text-sm text-gray-400">Peak Age Range</div>
          <div className="text-lg text-green-400 mt-1">{peak.count} calls</div>
        </div>
        
        <div className="flex items-end justify-center gap-1 h-16 w-full max-w-[200px]">
          {ageData.map((age, i) => {
            const height = (age.count / maxCount) * 100;
            const isPeak = age.range === peak.range;
            return (
              <div
                key={i}
                className={`flex-1 rounded-t-sm transition-all ${
                  isPeak 
                    ? 'bg-gradient-to-t from-green-600 to-green-400' 
                    : 'bg-gradient-to-t from-gray-700 to-gray-600'
                }`}
                style={{ height: `${height}%` }} />
            );
          })}
        </div>
      </div>
    );
  };

  const CompactGenderPreview = () => {
    const male = genderData.find(d => d.gender === 'Male') || { count: 0, percentage: 0 };
    const female = genderData.find(d => d.gender === 'Female') || { count: 0, percentage: 0 };
    
    return (
      <div className="h-full flex items-center justify-center gap-8">
        <div className="text-center">
          <div className="w-24 h-24 rounded-full bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center mb-3 shadow-lg shadow-blue-500/30">
            <span className="text-2xl font-bold text-white">{male.percentage}%</span>
          </div>
          <div className="text-xs text-gray-400 font-medium">Male</div>
          <div className="text-xs text-gray-600">{male.count.toLocaleString()} calls</div>
        </div>
        
        <div className="text-center">
          <div className="w-24 h-24 rounded-full bg-gradient-to-br from-pink-500 to-pink-700 flex items-center justify-center mb-3 shadow-lg shadow-pink-500/30">
            <span className="text-2xl font-bold text-white">{female.percentage}%</span>
          </div>
          <div className="text-xs text-gray-400 font-medium">Female</div>
          <div className="text-xs text-gray-600">{female.count.toLocaleString()} calls</div>
        </div>
      </div>
    );
  };

  const ExpansionModal = ({ chart, onClose }) => {
    if (!chart) return null;
    
    return (
      <div 
        className="fixed inset-0 flex items-center justify-center"
        style={{ zIndex: 99999, backgroundColor: 'rgba(0, 0, 0, 0.92)' }}
        onClick={onClose} >
        <div 
          className="bg-gray-900 rounded-xl p-6 border border-green-500/30 shadow-2xl flex flex-col"
          style={{ width: '92vw', height: '92vh', zIndex: 100000 }}
          onClick={e => e.stopPropagation()} >
          <div className="flex justify-between items-center mb-4 pb-3 border-b border-gray-800">
            <h2 className="text-2xl font-bold text-white">{chart.title}</h2>
            <button 
              onClick={onClose}
              className="text-gray-400 hover:text-white text-4xl leading-none font-light transition-colors" >
              X
            </button>
          </div>
          <div className="flex-1 overflow-hidden">
            {chart.component}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-950 overflow-y-auto" style={{ position: 'relative' }}>
      <AnimatedBackground />
      <Sidebar activeView={activeView} setActiveView={setActiveView} />
      
      <div 
        className="min-h-screen flex flex-col py-6 px-6 gap-6"
        style={{ marginLeft: '256px', position: 'relative', zIndex: 10 }} >

        {/* Filters & Call Count */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Calendar size={18} className="text-gray-500" />
            <input
              type="date"
              value={filters.dateRange.start}
              onChange={(e) => setFilters(prev => ({
                ...prev,
                dateRange: { ...prev.dateRange, start: e.target.value }
              }))}
              className="bg-gray-900/60 backdrop-blur-sm border border-gray-800/50 rounded-xl px-4 py-2 text-sm text-gray-300 focus:border-green-500/50 focus:outline-none transition-all"/>
            <span className="text-gray-600 text-sm">→</span>
            <input
              type="date"
              value={filters.dateRange.end}
              onChange={(e) => setFilters(prev => ({
                ...prev,
                dateRange: { ...prev.dateRange, end: e.target.value }
              }))}
              className="bg-gray-900/60 backdrop-blur-sm border border-gray-800/50 rounded-xl px-4 py-2 text-sm text-gray-300 focus:border-green-500/50 focus:outline-none transition-all" />
          </div>
          
          <div className="flex items-center gap-3">
            {['EMS', 'Fire', 'Traffic'].map(type => (
              <button
                key={type}
                onClick={() => handleTypeToggle(type)}
                className={`px-4 py-2 rounded-xl text-sm font-bold transition-all cursor-pointer ${
                  filters.types.includes(type)
                    ? 'bg-green-500/20 text-green-400 border border-green-500/30 shadow-lg shadow-green-500/10'
                    : 'bg-gray-900/30 text-gray-500 border border-gray-800/30 hover:border-gray-700'
                }`} >
                {type}
              </button>
            ))}
            <div className="ml-2 px-4 py-2 bg-gray-900/60 rounded-xl border border-gray-800/50">
              <span className="text-sm font-semibold text-white">{filteredData.length.toLocaleString()}</span>
              <span className="text-xs text-gray-500 ml-1">calls</span>
            </div>
          </div>
        </div>

        {/* KPI Cards Row */}
        <div className="grid grid-cols-4 gap-4">
          <CompactKPI 
            icon={Phone} 
            label="Total Calls" 
            value={kpis.totalCalls.toLocaleString()} 
            onClick={() => showDataTable('All Emergency Calls', filteredData)} />
          <CompactKPI 
            icon={Activity} 
            label="Most Common" 
            value={kpis.mostCommonType}
            onClick={() => showDataTable(`${kpis.mostCommonType} Incidents`, 
              filteredData.filter(d => d.emergencyType === kpis.mostCommonType)
            )} />
          <CompactKPI 
            icon={Users} 
            label="Average Age" 
            value={kpis.avgAge}
            onClick={() => showDataTable('Caller Age Data', filteredData)}  />
          <CompactKPI 
            icon={Clock} 
            label="Peak Hour" 
            value={kpis.peakHour}
            onClick={() => showDataTable(`Calls at ${kpis.peakHour}`,
              filteredData.filter(d => {
                const hour = new Date(d.timestamp).getHours();
                return hour === parseInt(kpis.peakHour.split(':')[0]);
              })
            )}
          />
        </div>

        {/* Hero Section */}
        <div className="grid grid-cols-2 gap-6" style={{ height: '480px' }}>
          <div className="bg-gradient-to-br from-gray-900/80 to-gray-800/80 backdrop-blur-sm rounded-2xl border border-gray-800/50 flex flex-col overflow-hidden shadow-2xl hover:border-green-500/30 transition-all">
            <div className="px-5 py-4 border-b border-gray-800/50 flex justify-between items-center">
              <h3 className="text-base font-semibold text-white">Call Volume Over Time</h3>
              <button 
                onClick={() => setExpandedChart({ 
                  title: 'Call Volume Over Time', 
                  component: <TimelineChart data={timelineData} hideTitle={true} /> 
                })}
                className="text-gray-500 hover:text-green-500 transition-colors p-2 hover:bg-gray-800/50 rounded-lg" >
                <Maximize2 size={16} />
              </button>
            </div>
            <div className="flex-1 p-5 overflow-hidden">
              <TimelineChart data={timelineData} compact={true} hideTitle={true} />
            </div>
          </div>

          <div className="bg-gradient-to-br from-gray-900/80 to-gray-800/80 backdrop-blur-sm rounded-2xl border border-gray-800/50 flex flex-col overflow-hidden shadow-2xl hover:border-green-500/30 transition-all">
            <div className="px-5 py-4 border-b border-gray-800/50 flex justify-between items-center">
              <h3 className="text-base font-semibold text-white">Geographic Distribution</h3>
              <button 
                onClick={() => setExpandedChart({ 
                  title: 'Geographic Distribution', 
                  component: <MapView filteredData={filteredData} heatmapPoints={heatmapPoints} dashboardFilters={filters} hideTitle={true} /> 
                })}
                className="text-gray-500 hover:text-green-500 transition-colors p-2 hover:bg-gray-800/50 rounded-lg" >
                <Maximize2 size={16} />
              </button>
            </div>
            <div className="flex-1 overflow-hidden">
              <MapView filteredData={filteredData} heatmapPoints={heatmapPoints} dashboardFilters={filters} compact={true} />
            </div>
          </div>
        </div>

        {/* Scroll Indicator */}
        <div className="flex justify-center py-2 -mt-2">
          <div className="flex flex-col items-center gap-2 animate-bounce">
            <span className="text-sm font-bold text-white">More Insights Below</span>
            <ChevronDown size={20} className="text-white" />
          </div>
        </div>

        {/* Demographics */}
        <div className="grid grid-cols-3 gap-6 pb-6 -mt-2" style={{ minHeight: '350px' }}>
          <div 
            className="bg-gradient-to-br from-gray-900/80 to-gray-800/80 backdrop-blur-sm rounded-2xl border border-gray-800/50 p-6 cursor-pointer hover:border-green-500/50 hover:shadow-xl hover:shadow-green-500/10 transition-all"
            onClick={() => setExpandedChart({ 
              title: 'Emergency Type Breakdown', 
              component: <TypePieChart data={typeData} hideTitle={true} /> 
            })} >
            <div className="flex justify-between items-center mb-3">
              <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wide">Emergency Types</h3>
              <Maximize2 size={12} className="text-gray-600" />
            </div>
            <CompactTypePreview />
          </div>

          <div 
            className="bg-gradient-to-br from-gray-900/80 to-gray-800/80 backdrop-blur-sm rounded-2xl border border-gray-800/50 p-6 cursor-pointer hover:border-green-500/50 hover:shadow-xl hover:shadow-green-500/10 transition-all"
            onClick={() => setExpandedChart({ 
              title: 'Age Distribution', 
              component: <AgeHistogram data={ageData} hideTitle={true} /> 
            })} >
            <div className="flex justify-between items-center mb-3">
              <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wide">Age Distribution</h3>
              <Maximize2 size={12} className="text-gray-600" />
            </div>
            <CompactAgePreview />
          </div>

          <div 
            className="bg-gradient-to-br from-gray-900/80 to-gray-800/80 backdrop-blur-sm rounded-2xl border border-gray-800/50 p-6 cursor-pointer hover:border-green-500/50 hover:shadow-xl hover:shadow-green-500/10 transition-all"
            onClick={() => setExpandedChart({ 
              title: 'Gender Distribution', 
              component: <GenderDonut data={genderData} hideTitle={true} /> 
            })} >
            <div className="flex justify-between items-center mb-3">
              <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wide">Gender Distribution</h3>
              <Maximize2 size={12} className="text-gray-600" />
            </div>
            <CompactGenderPreview />
          </div>
        </div>
      </div>

      <ExpansionModal 
        chart={expandedChart} 
        onClose={() => setExpandedChart(null)}  />

      {/* Drill-down Modal */}
      <Modal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        title={modalData.title} >
        <DataTable 
          data={modalData.data} 
          columns={modalData.columns} />
      </Modal>
    </div>
  );
};

export default Dashboard;