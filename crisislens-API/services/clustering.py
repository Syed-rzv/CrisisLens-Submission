import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from scipy.spatial import ConvexHull
from datetime import datetime
import json

# Simple in-memory cache (invalidates every 5 minutes)
cluster_cache = {}

class EmergencyClusterAnalyzer:
    #Performs DBSCAN clustering on emergency call geographic data.
    
    def __init__(self, eps_km=1.1, min_samples=10):
        self.eps = eps_km / 6371.0  # Convert km to radians for haversine
        self.min_samples = min_samples
        self.clusters = None
        self.cluster_stats = None
        
    def fit(self, data):
        #Cluster emergency calls by location.
        
        coords = np.radians(data[['lat', 'lon']].values)
        
        db = DBSCAN(eps=self.eps, min_samples=self.min_samples, metric='haversine', n_jobs=-1)
        data['cluster'] = db.fit_predict(coords)
        
        self.clusters = data
        self._calculate_statistics()
        
        return self
    
    def _calculate_statistics(self):
        #Generate insights for each cluster.
        stats = []
        
        for cluster_id in self.clusters['cluster'].unique():
            if cluster_id == -1:
                continue
                
            cluster_data = self.clusters[self.clusters['cluster'] == cluster_id]
            
            call_type_counts = cluster_data['call_type'].value_counts()
            primary_type = call_type_counts.index[0]
            primary_pct = (call_type_counts.iloc[0] / len(cluster_data)) * 100
            
            if 'hour' not in cluster_data.columns:
                cluster_data = cluster_data.copy()
                cluster_data['hour'] = pd.to_datetime(cluster_data['timestamp']).dt.hour
            peak_hour = cluster_data['hour'].mode()[0]
            
            severity_weights = {
                'Fire': 0.9, 'Medical Emergency': 0.85, 'Accident': 0.7, 'Assault': 0.75, 'Robbery': 0.65, 'Burglary': 0.5,
                'Vandalism': 0.3, 'Noise Complaint': 0.1 }
            
            cluster_size_factor = min(len(cluster_data) / 50, 2.0)
            weighted_severity = cluster_data.apply(
                lambda row: severity_weights.get(row['call_type'], 0.5), axis=1).mean()
            
            severity_score = min(10, weighted_severity * cluster_size_factor * 10)
            
            polygon = self._get_cluster_polygon(cluster_data)
            
            stats.append({
                'cluster_id': int(cluster_id),
                'call_count': len(cluster_data),
                'primary_type': primary_type,
                'primary_type_pct': round(primary_pct, 1),
                'peak_hour': int(peak_hour),
                'severity_score': round(severity_score, 1),
                'polygon': polygon,
                'center': {
                    'lat': float(cluster_data['lat'].mean()),
                    'lon': float(cluster_data['lon'].mean())
                }
            })
        
        self.cluster_stats = sorted(stats, key=lambda x: x['severity_score'], reverse=True)
    
    def _get_cluster_polygon(self, cluster_data):
        """Create convex hull boundary for cluster visualization."""
        points = cluster_data[['lat', 'lon']].values
        
        if len(points) < 3:
            return None
        
        try:
            hull = ConvexHull(points)
            polygon_coords = points[hull.vertices].tolist()
            polygon_coords.append(polygon_coords[0])
            return [[float(coord[0]), float(coord[1])] for coord in polygon_coords]
        except:
            return None
    
    def get_outliers(self):
        #outliers
        outliers = self.clusters[self.clusters['cluster'] == -1]
        
        return [{
            'lat': float(row['lat']),
            'lon': float(row['lon']),
            'call_type': row['call_type'],
            'timestamp': str(row['timestamp'])
        } for _, row in outliers.iterrows()]
    
    def get_temporal_analysis(self):
        # how clusters change between day/night
        daytime = self.clusters[
            (pd.to_datetime(self.clusters['timestamp']).dt.hour >= 6) & 
            (pd.to_datetime(self.clusters['timestamp']).dt.hour < 18)
        ]
        nighttime = self.clusters[
            (pd.to_datetime(self.clusters['timestamp']).dt.hour < 6) | 
            (pd.to_datetime(self.clusters['timestamp']).dt.hour >= 18)
        ]
        
        day_counts = daytime['cluster'].value_counts().to_dict()
        night_counts = nighttime['cluster'].value_counts().to_dict()
        
        temporal_shifts = []
        for cluster_id in self.cluster_stats:
            cid = cluster_id['cluster_id']
            day_calls = day_counts.get(cid, 0)
            night_calls = night_counts.get(cid, 0)
            
            if day_calls > 0:
                shift_pct = ((night_calls - day_calls) / day_calls) * 100
            else:
                shift_pct = 0
            
            temporal_shifts.append({
                'cluster_id': cid,
                'day_calls': day_calls,
                'night_calls': night_calls,
                'shift_percentage': round(shift_pct, 1)
            })
        
        return temporal_shifts
    
    def export_results(self):
        #Package all analysis results for API response.
        return {
            'clusters': self.cluster_stats,
            'outliers': self.get_outliers(),
            'temporal_analysis': self.get_temporal_analysis(),
            'summary': {'total_clusters': len(self.cluster_stats),'total_outliers': len(self.get_outliers()), 
            'highest_severity_cluster': self.cluster_stats[0]['cluster_id'] if self.cluster_stats else None }}


def analyze_emergency_clusters(data_df, time_range='all', min_severity=None):
    #Main function to run clustering analysis with caching.
    
    # Generate cache key (expires every 5 minutes)
    cache_key = f"{time_range}_{min_severity}_{datetime.now().strftime('%Y%m%d%H%M')[:-1]}"
    
    # Check cache first
    if cache_key in cluster_cache:
        print(f"cache hit: {time_range}/{min_severity}")
        return cluster_cache[cache_key]
    
    print(f"computing clusters: {time_range}/{min_severity}")
    
    #time filtering if needed
    if time_range == 'day':
        data_df = data_df[
            (pd.to_datetime(data_df['timestamp']).dt.hour >= 6) &
            (pd.to_datetime(data_df['timestamp']).dt.hour < 18)
        ]
    elif time_range == 'night':
        data_df = data_df[
            (pd.to_datetime(data_df['timestamp']).dt.hour < 6) |
            (pd.to_datetime(data_df['timestamp']).dt.hour >= 18)
        ]
    
    # Run clustering
    analyzer = EmergencyClusterAnalyzer(eps_km=1.1, min_samples=10)
    analyzer.fit(data_df)
    result = analyzer.export_results()
    
    cluster_cache[cache_key] = result
    
    # Clean old cache entries (keep only last 20)
    if len(cluster_cache) > 20:
        oldest_key = list(cluster_cache.keys())[0]
        del cluster_cache[oldest_key]
    
    return result