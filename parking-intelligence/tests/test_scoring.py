import unittest
import pandas as pd
import json
import yaml
import os
from src.scoring.heuristic import calculate_zone_scores

class TestScoring(unittest.TestCase):
    def setUp(self):
        os.makedirs("config", exist_ok=True)
        with open("config/scoring_weights.yaml", "w") as f:
            yaml.dump({
                "w_volume": 0.4,
                "w_heavy": 0.25,
                "w_road_class": 0.2,
                "w_time_conc": 0.15
            }, f)
            
        self.raw_df = pd.DataFrame({
            'vehicle_type': ['LMV', 'HGV', 'HGV', 'TWO WHEELER', 'LMV', 'LMV'],
            'violation_type': ['PARKING', 'MAIN ROAD', 'MAIN ROAD', 'PARKING', 'PARKING', 'PARKING'],
            'created_datetime': [
                '2023-01-01 10:00:00', '2023-01-01 10:15:00', '2023-01-01 10:30:00',
                '2023-01-01 14:00:00', '2023-01-01 15:00:00', '2023-01-01 16:00:00'
            ]
        })
        
    def test_scoring_damping_logic(self):
        # Create a zone with exactly 500 violations (damping = 1.0)
        zone1_indices = [0, 1, 2] # 3 items, 2 are HGV, 2 are MAIN ROAD. 
        # But we will fake the violation_count to test damping
        
        zones_gdf = pd.DataFrame({
            'zone_id': [1, 2],
            'violation_count': [500, 50],
            'indices': [zone1_indices, [3, 4, 5]]
        })
        
        scored = calculate_zone_scores(zones_gdf, self.raw_df, "config/scoring_weights.yaml")
        
        z1 = scored.iloc[0]
        z2 = scored.iloc[1]
        
        # z1 has 500 count, damping should be 1.0
        b1 = json.loads(z1['score_breakdown'])
        self.assertEqual(b1['damping_factor'], 1.0)
        self.assertEqual(b1['heavy_ratio'], 2/3) # 2 HGVs out of 3
        self.assertEqual(b1['road_class_weight'], 1.0)
        
        # z2 has 50 count, damping should be 0.1
        b2 = json.loads(z2['score_breakdown'])
        self.assertEqual(b2['damping_factor'], 0.1)
        
        # Verify the actual outcome: high-violation zone scores higher
        self.assertGreater(z1['score'], z2['score'])

    def test_scoring_extreme_bug_case(self):
        # Reproduces the real-world bug: 
        # Upparpet Area (23034 violations) vs Electronic City Area (7 violations)
        # Electronic City maxes out all ratios (heavy_ratio=1, road_class=1, time_conc=1)
        # Upparpet has typical low ratios but massive volume.
        
        # We don't need real indices, just the DataFrame structure
        zones_gdf = pd.DataFrame({
            'zone_id': [1, 2],
            'violation_count': [23034, 7],
            'indices': [[0], [1]] # just dummy references
        })
        
        # Create a df that ensures zone 2 hits max ratios
        raw_df = pd.DataFrame({
            'vehicle_type': ['LMV', 'HGV'], # zone 1 = LMV, zone 2 = HGV (heavy_ratio=1.0)
            'violation_type': ['PARKING', 'MAIN ROAD'], # zone 2 = MAIN ROAD (road_class=1.0)
            'created_datetime': ['2023-01-01 10:00:00', '2023-01-01 10:00:00'] # time_conc=1.0
        })
        
        scored = calculate_zone_scores(zones_gdf, raw_df, "config/scoring_weights.yaml")
        
        upparpet_score = scored.iloc[0]['score']
        ecity_score = scored.iloc[1]['score']
        
        # The core assertion: Upparpet should score meaningfully higher than E-City 
        # despite E-City maxing out all secondary metrics, due to the damping factor.
        self.assertGreater(upparpet_score, ecity_score)
        
        # Assert it's greater by a wide margin (at least double)
        self.assertGreater(upparpet_score, ecity_score * 2)

if __name__ == '__main__':
    unittest.main()
