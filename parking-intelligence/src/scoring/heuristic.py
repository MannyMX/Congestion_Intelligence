import yaml
import pandas as pd
import numpy as np
import json

def get_scoring_weights(config_path: str = "config/scoring_weights.yaml") -> dict:
    with open(config_path, 'r') as f:
        weights = yaml.safe_load(f)
    
    total = sum(weights.values())
    return {k: v / total for k, v in weights.items()}

def calculate_zone_scores(zones_gdf: pd.DataFrame, df: pd.DataFrame, config_path: str = "config/scoring_weights.yaml") -> pd.DataFrame:
    weights = get_scoring_weights(config_path)
    max_volume = zones_gdf['violation_count'].max() or 1
    
    HEAVY_CLASSES = {'LGV', 'HGV', 'LORRY/GOODS VEHICLE', 'PRIVATE BUS', 'BUS (BMTC/KSRTC)', 'TEMPO'}
    
    scores = []
    score_breakdowns = []
    
    for idx, row in zones_gdf.iterrows():
        norm_volume = row['violation_count'] / max_volume
        zone_df = df.loc[row['indices']] if 'indices' in row else pd.DataFrame()
        
        heavy_ratio = 0.0
        if not zone_df.empty and 'vehicle_type' in zone_df.columns:
            heavy_count = zone_df['vehicle_type'].isin(HEAVY_CLASSES).sum()
            heavy_ratio = heavy_count / len(zone_df)
            
        road_class_weight = 0.0
        if not zone_df.empty and 'violation_type' in zone_df.columns:
            has_main_road = zone_df['violation_type'].apply(lambda x: 'MAIN ROAD' in str(x).upper() or 'CROSSING' in str(x).upper()).any()
            if has_main_road:
                road_class_weight = 1.0
                
        time_conc_index = 0.0
        if not zone_df.empty and 'created_datetime' in zone_df.columns:
            hours = pd.to_datetime(zone_df['created_datetime']).dt.hour
            hour_counts = hours.value_counts(normalize=True)
            entropy = -(hour_counts * np.log(hour_counts + 1e-9)).sum()
            max_entropy = np.log(24)
            time_conc_index = 1.0 - (entropy / max_entropy)
            time_conc_index = max(0.0, time_conc_index)
            
        damping_factor = min(1.0, row['violation_count'] / 500.0)

        score = (
            weights['w_volume'] * norm_volume +
            (weights['w_heavy'] * heavy_ratio * damping_factor) +
            (weights['w_road_class'] * road_class_weight * damping_factor) +
            (weights['w_time_conc'] * time_conc_index * damping_factor)
        )
        
        breakdown = {
            "norm_volume": float(norm_volume),
            "heavy_ratio": float(heavy_ratio),
            "road_class_weight": float(road_class_weight),
            "time_conc_index": float(time_conc_index),
            "damping_factor": float(damping_factor)
        }
        
        scores.append(score)
        score_breakdowns.append(json.dumps(breakdown))
        
    zones_gdf['score'] = scores
    zones_gdf['score_breakdown'] = score_breakdowns
    
    if 'indices' in zones_gdf.columns:
        zones_gdf = zones_gdf.drop(columns=['indices'])
        
    return zones_gdf
