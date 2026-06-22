import duckdb
import json
import os

def get_breakdown():
    db_path = os.environ.get("DUCKDB_PATH", "/app/data/processed/parking_intelligence.duckdb")
    conn = duckdb.connect(db_path)
    
    # Upparpet Area
    upparpet = conn.execute("""
        SELECT police_station, violation_count, score, score_breakdown
        FROM zones 
        WHERE police_station LIKE '%UPPARPET%' OR police_station LIKE '%Upparpet%'
        ORDER BY violation_count DESC LIMIT 1
    """).fetchone()
    
    # Byatarayanapura anomaly
    anomaly = conn.execute("""
        SELECT police_station, violation_count, score, score_breakdown
        FROM zones 
        WHERE violation_count = 44 AND police_station LIKE '%Byata%'
        ORDER BY score DESC LIMIT 1
    """).fetchone()
    
    if anomaly:
        print(f"Station: {anomaly[0]}, Violations: {anomaly[1]}, Score: {anomaly[2]:.4f}")
        print("Breakdown:", json.dumps(json.loads(anomaly[3]), indent=2))
    
    print("--- Upparpet Area ---")
    if upparpet:
        print(f"Station: {upparpet[0]}, Violations: {upparpet[1]}, Score: {upparpet[2]:.4f}")
        print("Breakdown:", json.dumps(json.loads(upparpet[3]), indent=2))
    else:
        print("Not found")
    
    print("\n--- Electronic City Area ---")
    if ecity:
        print(f"Station: {ecity[0]}, Violations: {ecity[1]}, Score: {ecity[2]:.4f}")
        print("Breakdown:", json.dumps(json.loads(ecity[3]), indent=2))
    else:
        print("Not found")

if __name__ == "__main__":
    get_breakdown()
