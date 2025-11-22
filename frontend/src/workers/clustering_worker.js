//Background thread, doesn't block UI

self.onmessage = function(e) {
    const { data, params } = e.data;
    
    console.log(' Worker: Starting clustering...', data.length, 'points');
    
    try {
      //  DBSCAN clustering
      const clusters = performDBSCAN(data, params);
      
      console.log('Worker: Clustering complete!', clusters.length, 'clusters');
      
      // Send results back to main thread
      self.postMessage({
        status: 'success',
        clusters: clusters,
        outliers: clusters.filter(c => c.isOutlier)
      });
      
    } catch (error) {
      console.error('Worker: Clustering failed', error);
      self.postMessage({
        status: 'error',
        error: error.message
      });
    }
  };
  
  // DBSCAN implementation for Web Worker
  function performDBSCAN(points, params) {
    const { eps = 0.01, minSamples = 10 } = params;
        
    const clusters = [];
    const visited = new Set();
    const noise = new Set();
    let clusterId = 0;
    
    function getNeighbors(pointIdx) {
      const neighbors = [];
      const point = points[pointIdx];
      
      for (let i = 0; i < points.length; i++) {
        if (i === pointIdx) continue;
        
        const distance = haversineDistance(
          point.latitude, point.longitude,
          points[i].latitude, points[i].longitude
        );
        
        if (distance <= eps) {
          neighbors.push(i);
        }
      }
      
      return neighbors;
    }
    
    function expandCluster(pointIdx, neighbors, clusterId) {
      const cluster = {
        id: clusterId,
        points: [points[pointIdx]],
        center: null,
        isOutlier: false
      };
      
      visited.add(pointIdx);
      
      for (let i = 0; i < neighbors.length; i++) {
        const neighborIdx = neighbors[i];
        
        if (!visited.has(neighborIdx)) {
          visited.add(neighborIdx);
          const neighborNeighbors = getNeighbors(neighborIdx);
          
          if (neighborNeighbors.length >= minSamples) {
            neighbors = neighbors.concat(neighborNeighbors);
          }
        }
        
        cluster.points.push(points[neighborIdx]);
      }
      
      // Calculating cluster center
      const avgLat = cluster.points.reduce((sum, p) => sum + p.latitude, 0) / cluster.points.length;
      const avgLng = cluster.points.reduce((sum, p) => sum + p.longitude, 0) / cluster.points.length;
      
      cluster.center = { latitude: avgLat, longitude: avgLng };
      
      return cluster;
    }
    
    // Main DBSCAN loop
    for (let i = 0; i < points.length; i++) {
      if (visited.has(i)) continue;
      
      const neighbors = getNeighbors(i);
      
      if (neighbors.length < minSamples) {
        noise.add(i);
        clusters.push({
          id: -1,
          points: [points[i]],
          center: { latitude: points[i].latitude, longitude: points[i].longitude },
          isOutlier: true
        });
      } else {
        const cluster = expandCluster(i, neighbors, clusterId++);
        clusters.push(cluster);
      }
    }
    
    return clusters;
  }
  
  // Haversine distance formula 
  function haversineDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // Earth's radius in km
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) + Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    
    return R * c;
  }