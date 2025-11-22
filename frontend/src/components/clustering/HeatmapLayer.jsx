import { useEffect, useRef } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet.heat';

const HeatmapLayer = ({ data, intensity = 0.6, radius = 25, blur = 15, minSeverity = 0 }) => {
  const map = useMap();
  const heatLayerRef = useRef(null);

  useEffect(() => {
    if (!data || data.length === 0) return;
    if (!map) return;

    if (heatLayerRef.current) {
      map.removeLayer(heatLayerRef.current);
      heatLayerRef.current = null;
    }

    const addHeatmap = () => {
      try {
        let filteredData = data;

        if (minSeverity > 0) {
          const minIntensity = 0.4 + (minSeverity / 10) * 0.5;

          filteredData = data.filter(point => point[2] >= minIntensity);

          if (minSeverity > 5) {
            filteredData = filteredData.map(point => [
              point[0], point[1], Math.min(1.0, point[2] * 1.3) ]); }

          console.log(`Severity ${minSeverity}: ${filteredData.length}/${data.length} points (intensity ≥ ${minIntensity.toFixed(2)})`); }

        if (filteredData.length === 0) {
          console.log('No points match severity threshold');
          return; }

        const maxValue = 0.3;

        heatLayerRef.current = L.heatLayer(filteredData, { radius: 15, blur: 25, maxZoom: 17, max: 0.2, minOpacity: 0.1,
          gradient: {
            0.4: '#22c55e',
            0.6: '#eab308',
            0.75: '#f97316',
            0.85: '#ef4444'
          }
        });

        heatLayerRef.current.addTo(map);

        setTimeout(() => {
          if (map) {
            map.invalidateSize();
          }
        }, 50);
      } catch (error) {
        console.error('Heatmap error:', error);
      }
    };

    const timer = setTimeout(addHeatmap, 100);

    return () => {
      clearTimeout(timer);
      if (heatLayerRef.current && map.hasLayer(heatLayerRef.current)) {
        map.removeLayer(heatLayerRef.current);
        heatLayerRef.current = null;
      }
    };
  }, [map, data, radius, blur, minSeverity]);

  return null;
};

export default HeatmapLayer;