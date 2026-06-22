import pandas as pd
import json
import ast
import argparse
from pathlib import Path
from src.data.dao import ParkingDAO
from src.zones.clusterer import generate_zones
from src.scoring.heuristic import calculate_zone_scores

def parse_list_col(val):
    if pd.isna(val):
        return []
    try:
        return ast.literal_eval(val)
    except (ValueError, SyntaxError):
        try:
            return json.loads(val)
        except json.JSONDecodeError:
            return [str(val)]

def load_and_clean_data(csv_path: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    print(f"Loading data from {csv_path}...")
    df = pd.read_csv(csv_path)
    
    df['created_datetime'] = pd.to_datetime(df['created_datetime'], utc=True, errors='coerce')
    df['violation_type'] = df['violation_type'].apply(parse_list_col)
    df['offence_code'] = df['offence_code'].apply(parse_list_col)
    
    valid_coords = (
        df['latitude'].between(12.7, 13.2) & 
        df['longitude'].between(77.3, 77.9)
    )
    
    outliers = df[~valid_coords]
    print(f"Quarantined {len(outliers)} rows with out-of-bounds coordinates.")
    
    df = df[valid_coords]
    
    all_df = df.copy()
    clean_df = df[df['validation_status'] == 'approved'].copy()
    print(f"Approved ground-truth rows: {len(clean_df)}")
    
    all_df['violation_type'] = all_df['violation_type'].apply(json.dumps)
    all_df['offence_code'] = all_df['offence_code'].apply(json.dumps)
    
    clean_df['violation_type_list'] = clean_df['violation_type']
    clean_df['violation_type'] = clean_df['violation_type'].apply(json.dumps)
    clean_df['offence_code'] = clean_df['offence_code'].apply(json.dumps)
    
    clean_df['vehicle_type'] = clean_df['vehicle_type'].fillna('UNKNOWN')
    clean_df['police_station'] = clean_df['police_station'].fillna('UNKNOWN')
    
    return all_df, clean_df

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=str, default="data/raw/jan_to_may_police_violation.csv")
    parser.add_argument("--db", type=str, default="data/processed/parking_intelligence.duckdb")
    args = parser.parse_args()
    
    if not Path(args.csv).exists():
        print(f"Error: CSV file not found at {args.csv}")
        return

    all_df, clean_df = load_and_clean_data(args.csv)
    
    print("Running spatial clustering (DBSCAN)...")
    zones_gdf = generate_zones(clean_df)
    print(f"Identified {len(zones_gdf)} zones (hotspots).")
    
    print("Calculating congestion proxy scores...")
    zones_gdf = calculate_zone_scores(zones_gdf, clean_df)
    
    print("Saving to DuckDB...")
    dao = ParkingDAO(db_path=args.db)
    dao.save_violations(all_df)
    dao.save_zones(zones_gdf)
    dao.close()
    print("Data load complete!")

if __name__ == "__main__":
    main()
