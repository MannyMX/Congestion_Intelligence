import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import MultiPoint, Point
from sklearn.cluster import DBSCAN
import yaml

class DBSCANClusterer:
    def __init__(self, eps_meters: float, min_samples: int):
        self.eps = eps_meters / 6371000.0 # Convert to radians for haversine
        self.min_samples = min_samples

    def fit_predict(self, df: pd.DataFrame) -> pd.DataFrame:
        coords = np.radians(df[['latitude', 'longitude']].values)
        model = DBSCAN(eps=self.eps, min_samples=self.min_samples, algorithm='ball_tree', metric='haversine')
        return model.fit_predict(coords)

def generate_zones(df: pd.DataFrame, config_path: str = "config/dbscan_params.yaml") -> gpd.GeoDataFrame:
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
        
    params = config.get('dbscan', {'eps': 50.0, 'min_samples': 5})
    clusterer = DBSCANClusterer(eps_meters=params['eps'], min_samples=params['min_samples'])
    
    df['cluster_id'] = clusterer.fit_predict(df)
    
    # DBSCAN label -1 means noise
    clusters = df[df['cluster_id'] != -1].copy()
    
    zones_data = []
    for cid, group in clusters.groupby('cluster_id'):
        points = [Point(xy) for xy in zip(group.longitude, group.latitude)]
        multipoint = MultiPoint(points)
        
        geom = multipoint.convex_hull
        if geom.geom_type in ['Point', 'LineString']:
            geom = geom.buffer(0.0002) 

        centroid = geom.centroid
        
        top_vehicle = group['vehicle_type'].mode().iloc[0] if not group['vehicle_type'].mode().empty else "UNKNOWN"
        
        tag_col = 'violation_type_list' if 'violation_type_list' in group.columns else 'violation_type'
        if isinstance(group[tag_col].iloc[0], list):
            exploded = group[tag_col].explode()
            top_tag = exploded.mode().iloc[0] if not exploded.mode().empty else "UNKNOWN"
        else:
            top_tag = group[tag_col].mode().iloc[0] if not group[tag_col].mode().empty else "UNKNOWN"
            
        station = group['police_station'].mode().iloc[0] if not group['police_station'].mode().empty else "UNKNOWN"
        
        zones_data.append({
            'cluster_id': cid,
            'centroid_lat': centroid.y,
            'centroid_lon': centroid.x,
            'violation_count': len(group),
            'dominant_vehicle_type': top_vehicle,
            'dominant_violation_tag': top_tag,
            'police_station': station,
            'geometry': geom,
            'indices': group.index.tolist()
        })
        
    gdf = gpd.GeoDataFrame(zones_data, crs="EPSG:4326")
    return gdf
