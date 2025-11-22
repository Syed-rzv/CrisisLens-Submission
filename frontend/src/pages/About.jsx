import { BarChart3, Upload, TrendingUp, Clock, AlertTriangle, Phone, HelpCircle } from 'lucide-react';

export default function About() {
  const features = [
    {
      icon: BarChart3,
      title: 'Dashboard Overview',
      description: 'Navigate to the Dashboard tab to view data visualizations of emergency calls. Filter data by date, location, and type of emergency.'
    },
    {
      icon: Phone,
      title: 'Submit Calls',
      description: 'Log new emergency calls directly into the system. The system automatically classifies and enriches incident data.'
    },
    {
      icon: Clock,
      title: 'Temporal Analysis',
      description: 'Explore when emergencies occur most frequently. View peak hours, seasonal trends, and patterns by emergency type.'
    },
    {
      icon: TrendingUp,
      title: 'Forecasting',
      description: 'View predictions for future emergency call volumes. Helps with resource planning and preparedness.'
    },
    {
      icon: AlertTriangle,
      title: 'Anomaly Detection',
      description: 'Identify unusual patterns in emergency call data. The system flags days with unexpected call volumes or distributions.'
    },
    {
      icon: Upload,
      title: 'Upload Dataset',
      description: 'Import historical emergency call data from CSV or Excel files. The system automatically processes and classifies uploaded records.'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-4">About CrisisLens</h1>

        <div className="mb-12">
          <h2 className="text-xl font-semibold mb-4">How to Use the Dashboard</h2>
          <p className="text-gray-300 leading-relaxed">
            CrisisLens is a powerful tool designed to help emergency response teams analyze and understand emergency call data. 
            Here's a quick guide to get you started:
          </p>
        </div>

        <div className="space-y-6 mb-12">
          {features.map((feature, idx) => {
            const Icon = feature.icon;
            return (
              <div key={idx} className="flex gap-4">
                <div className="flex-shrink-0 w-12 h-12 bg-gray-800 rounded-lg flex items-center justify-center">
                  <Icon className="w-6 h-6 text-green-500" />
                </div>
                <div>
                  <h3 className="font-semibold text-lg mb-1">{feature.title}</h3>
                  <p className="text-gray-400 text-sm leading-relaxed">{feature.description}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}