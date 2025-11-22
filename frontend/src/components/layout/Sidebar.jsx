import React from 'react';
import { Home, Upload, Filter, TrendingUp, Info, Activity, Phone, Clock, AlertTriangle, LogOut } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const Sidebar = ({ activeView, setActiveView }) => {
  const { user, logout } = useAuth();

  const menuItems = [
    { id: 'dashboard', icon: Home, label: 'Dashboard' },
    { id: 'submit', icon: Phone, label: 'Submit Call' },
    { id: 'temporal', icon: Clock, label: 'Temporal Analysis' },
    { id: 'forecasting', icon: TrendingUp, label: 'Forecasting' },
    { id: 'anomalies', icon: AlertTriangle, label: 'Anomalies' },
    //{ id: 'upload', icon: Upload, label: 'Upload Dataset', adminOnly: true },
    { id: 'about', icon: Info, label: 'About' }
  ];

  return (
    <div className="fixed left-0 top-0 h-screen w-64 bg-gray-900 border-r border-gray-800 overflow-y-auto shadow-2xl shadow-black/50 z-50 flex flex-col">
      <div className="px-6 pt-6 mb-8 pb-6 border-b border-gray-800">
        <div className="flex items-center gap-3">
          <Activity className="w-6 h-6 text-green-500" />
          <h1 className="text-xl font-bold text-green-500">CrisisLens</h1>
        </div>
        <p className="text-xs text-gray-400 mt-2">Emergency Analytics</p>
      </div>

      <nav className="space-y-2 px-6 pb-6 flex-1">
        {menuItems.map((item) => {
          if (item.adminOnly && user?.role !== 'admin') {
            return null;
          }

          const Icon = item.icon;
          return (
            <button
              key={item.id}
              onClick={() => setActiveView(item.id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                activeView === item.id
                  ? 'bg-green-500 text-white shadow-lg shadow-green-500/30'
                  : 'text-gray-400 hover:bg-gray-800 hover:text-green-500'
              }`}  >
              <Icon className="w-5 h-5 flex-shrink-0" />
              <span className="font-medium text-left">{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div className="px-6 pb-6 border-t border-gray-800 pt-4">
        <button
          onClick={logout}
          className="w-full flex items-center gap-3 px-4 py-3 text-gray-400 hover:text-red-400 hover:bg-gray-800 rounded-lg transition-all" >
          <LogOut className="w-5 h-5 flex-shrink-0" />
          <span className="font-medium text-left">Logout</span>
        </button>
      </div>
    </div>
  );
};

export default Sidebar;