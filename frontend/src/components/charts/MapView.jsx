import { useState, useMemo, useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { useClusterData, useHeatmapData } from '../../hooks/useClusterData';
import HeatmapLayer from '../clustering/HeatmapLayer';
import ClusterPolygon from '../clustering/ClusterPolygon';
import MapControls from '../clustering/MapControls';

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const outlierIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-yellow.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

const redPinIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

const ZoomHandler = ({ onZoomChange }) => {
  const map = useMap();
  
  useEffect(() => {
    if (map) {
      onZoomChange(map.getZoom());
    }
  }, [map, onZoomChange]);

  useMapEvents({
    zoomend: () => {
      onZoomChange(map.getZoom());
    }
  });

  return null;
};

const VisiblePinsLayer = ({ heatmapData, redPinIcon, minSeverity = 0  }) => {
  const map = useMap();
  const [visiblePins, setVisiblePins] = useState([]);

  useMapEvents({
    moveend: () => {
      updateVisiblePins();
    },
    zoomend: () => {
      updateVisiblePins();
    }
  });

  useEffect(() => {
    updateVisiblePins();
  }, [heatmapData, minSeverity]);

  const updateVisiblePins = () => {
    if (!map || !heatmapData || heatmapData.length === 0) return;
    
    const bounds = map.getBounds();
    const visible = heatmapData.filter(point => {
      const inBounds = bounds.contains([point[0], point[1]]);
        const severity = point[2] * 10;
        const meetsMinSeverity = severity >= minSeverity;
        return inBounds && meetsMinSeverity;
    });

    
    setVisiblePins(visible.slice(0, 500));
  };

  return (
    <>
      {visiblePins.map((point, idx) => (
        <Marker
          key={`pin-${point[0]}-${point[1]}-${idx}`}
          position={[point[0], point[1]]}
          icon={redPinIcon} >
          <Popup>
            <div className="p-2">
              <h4 className="font-bold text-sm text-gray-800 mb-2">
                Emergency Call
              </h4>
              <div className="text-xs space-y-1">
                <div>
                  <span className="text-gray-600">Severity:</span>{' '}
                  <span className="font-semibold">{(point[2] * 10).toFixed(1)}/10</span>
                </div>
                <div className="text-gray-500 text-[10px] mt-2">
                  {point[0].toFixed(4)}, {point[1].toFixed(4)}
                </div>
              </div>
            </div>
          </Popup>
        </Marker>
      ))}
    </>
  );
};

const MapView = ({ filteredData = [], heatmapPoints = [], dashboardFilters = null, initialCenter = [40.7128, -74.0060], initialZoom = 11, compact = false }) => {
  const [currentZoom, setCurrentZoom] = useState(initialZoom);
  const [layerSettings, setLayerSettings] = useState({
    showHeatmap: true,
    showClusters: true,
    showOutliers: false,
    timeRange: 'all',
    minSeverity: 0
  });

  const ZOOM_THRESHOLD = 15;

  const clusterParams = useMemo(() => ({
    timeRange: layerSettings.timeRange,
    minSeverity: layerSettings.minSeverity > 0 ? layerSettings.minSeverity : null
  }), [layerSettings.timeRange, layerSettings.minSeverity]);

  const { clusters, outliers, loading: clusterLoading, error: clusterError } = useClusterData(
    clusterParams.timeRange,
    clusterParams.minSeverity,
    dashboardFilters
  );

  const { heatmapData, loading: heatmapLoading } = useHeatmapData(dashboardFilters);

  const mapRef = useRef(null);

  const mapCenter = useMemo(() => {
    if (!clusters || clusters.length === 0) {
      return [40.2, -75.4];
    }
    
    let totalLat = 0;
    let totalLng = 0;
    let validClusters = 0;
    
    clusters.forEach(c => {
      let lat, lng;
      
      if (Array.isArray(c.centroid)) {
        lat = c.centroid[0];
        lng = c.centroid[1];
      } else if (c.centroid?.lat && c.centroid?.lon) {
        lat = c.centroid.lat;
        lng = c.centroid.lon;
      } else if (c.centroid?.lat && c.centroid?.lng) {
        lat = c.centroid.lat;
        lng = c.centroid.lng;
      }
      
      if (lat && lng && lat !== 0 && lng !== 0) {
        totalLat += lat;
        totalLng += lng;
        validClusters++;
      }
    });
    
    if (validClusters === 0) {
      return [40.2, -75.4];
    }
    
    return [totalLat / validClusters, totalLng / validClusters];
  }, [clusters]);

  useEffect(() => {
    if (!clusterLoading && clusters.length > 0 && mapRef.current) {
      setTimeout(() => {
        if (mapRef.current) {
          mapRef.current.invalidateSize();
        }
      }, 100);
    }
  }, [clusterLoading, clusters]);

  const filteredClusters = useMemo(() => {
    return clusters.filter(c => c.severity_score >= layerSettings.minSeverity);
  }, [clusters, layerSettings.minSeverity]);

  const handleLayerToggle = (newSettings) => {
    if (clusterLoading && (newSettings.timeRange !== layerSettings.timeRange)) {
      console.log('Please wait for clusters to finish loading');
      return;
    }
    setLayerSettings(newSettings);
  };

  if (clusterError) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <p className="text-red-600 font-semibold mb-2">⚠️ Error Loading Clusters</p>
          <p className="text-sm text-gray-600">{clusterError}</p>
          <p className="text-xs text-gray-500 mt-2">The backend may be restarting. Try again in a moment.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="relative w-full h-full" style={{ minHeight: '600px' }}>
      {(clusterLoading || heatmapLoading) && (
        <div className="absolute inset-0 bg-white bg-opacity-75 z-[2000] flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-2"></div>
            <p className="text-sm text-gray-600">Analyzing clusters...</p>
            <p className="text-xs text-gray-500 mt-1">This may take a moment</p>
          </div>
        </div>
      )}

      {!compact && <MapControls onLayerToggle={handleLayerToggle} activeFilters={{ ...layerSettings, loading: clusterLoading }} />}

      <MapContainer
        center={mapCenter}
        zoom={initialZoom}
        style={{ height: '100%', width: '100%' }}
        className="z-0"
        ref={mapRef} >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

        <ZoomHandler onZoomChange={setCurrentZoom} />

        {currentZoom < ZOOM_THRESHOLD && layerSettings.showHeatmap && heatmapData.length > 0 && (
          <HeatmapLayer
            data={heatmapData}
            minSeverity={layerSettings.minSeverity} />
        )}

        {currentZoom >= ZOOM_THRESHOLD && heatmapData.length > 0 && (
          <VisiblePinsLayer heatmapData={heatmapData} redPinIcon={redPinIcon} minSeverity={layerSettings.minSeverity}  />
        )}

        {layerSettings.showClusters && filteredClusters.map((cluster) => (
          <ClusterPolygon key={cluster.cluster_id} cluster={cluster} />
        ))}

        {layerSettings.showOutliers && outliers.map((outlier, idx) => (
          <Marker
            key={`outlier-${idx}`}
            position={[outlier.lat, outlier.lon]}
            icon={outlierIcon} >
            <Popup>
              <div className="p-2">
                <h4 className="font-bold text-sm text-gray-800 mb-2">
                  ⚠️ Isolated Call
                </h4>
                <div className="text-xs space-y-1">
                  <div>
                    <span className="text-gray-600">Type:</span>{' '}
                    <span className="font-semibold">{outlier.call_type}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Time:</span>{' '}
                    <span className="font-semibold">
                      {new Date(outlier.timestamp).toLocaleString()}
                    </span>
                  </div>
                </div>
                <div className="mt-2 pt-2 border-t border-gray-200 text-xs text-orange-600">
                  This area may be underserved
                </div>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>

      {!clusterLoading && !compact && (
        <div className="fixed bottom-4 left-4 z-[1100] bg-white rounded-lg shadow-lg p-3 w-auto min-w-[140px]">
          <div className="text-xs space-y-1 whitespace-nowrap">
            <div className="font-semibold text-gray-800 mb-1">Quick Stats</div>
            <div className="text-gray-600">
              Clusters: <span className="font-semibold text-gray-900">{filteredClusters.length}</span>
            </div>
            {layerSettings.showOutliers && (
              <div className="text-gray-600">
                Outliers: <span className="font-semibold text-gray-900">{outliers.length}</span>
              </div>
            )}
            <div className="text-gray-600">
              Time: <span className="font-semibold text-gray-900 capitalize">{layerSettings.timeRange}</span>
            </div>
            <div className="text-gray-600 text-[10px] mt-1 pt-1 border-t border-gray-200">
              Zoom: {currentZoom < ZOOM_THRESHOLD ? 'Heatmap' : 'Pins'}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MapView;