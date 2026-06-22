import unittest
import pandas as pd
import geopandas as gpd
from src.zones.clusterer import DBSCANClusterer, generate_zones
import yaml
import os

class TestClusterer(unittest.TestCase):
    def setUp(self):
        # Create dummy config
        os.makedirs("config", exist_ok=True)
        with open("config/dbscan_params.yaml", "w") as f:
            yaml.dump({"dbscan": {"eps": 50.0, "min_samples": 3}}, f)
            
        # Create synthetic data with 2 distinct clusters
        # Cluster 1: near (12.97, 77.59)
        # Cluster 2: near (12.98, 77.60)
        self.df = pd.DataFrame({
            'latitude': [12.9700, 12.9701, 12.9702, 12.9800, 12.9801, 12.9802, 13.0],
            'longitude': [77.5900, 77.5901, 77.5902, 77.6000, 77.6001, 77.6002, 77.7],
            'vehicle_type': ['LMV', 'LMV', 'HGV', 'TWO WHEELER', 'TWO WHEELER', 'LMV', 'LMV'],
            'violation_type_list': [['WRONG PARKING'], ['WRONG PARKING'], ['NO PARKING'], ['NO PARKING'], ['NO PARKING'], ['WRONG PARKING'], ['NO PARKING']],
            'police_station': ['S1', 'S1', 'S1', 'S2', 'S2', 'S2', 'S3']
        })

    def test_clustering_identifies_clusters(self):
        gdf = generate_zones(self.df, config_path="config/dbscan_params.yaml")
        # Should identify 2 clusters (the point at 13.0, 77.7 is noise)
        self.assertEqual(len(gdf), 2)
        
        # Verify cluster 1 logic
        c1 = gdf[gdf['police_station'] == 'S1'].iloc[0]
        self.assertEqual(c1['violation_count'], 3)
        self.assertEqual(c1['dominant_vehicle_type'], 'LMV')
        
        # Verify cluster 2 logic
        c2 = gdf[gdf['police_station'] == 'S2'].iloc[0]
        self.assertEqual(c2['violation_count'], 3)

if __name__ == '__main__':
    unittest.main()
