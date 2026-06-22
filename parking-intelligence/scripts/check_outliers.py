import duckdb
import os

def check_outliers():
    db_path = os.environ.get("DUCKDB_PATH", "/app/data/processed/parking_intelligence.duckdb")
    conn = duckdb.connect(db_path)
    
    print("=== TOP 10 ZONES OVERALL ===")
    top_all = conn.execute("""
        SELECT police_station, violation_count, score
        FROM zones 
        ORDER BY score DESC LIMIT 10
    """).fetchall()
    
    for row in top_all:
        print(f"Station: {row[0]:<20} | Violations: {row[1]:<6} | Score: {row[2]:.4f}")
        
    print("\n=== TOP 10 ZONES (violation_count < 50) ===")
    top_small = conn.execute("""
        SELECT police_station, violation_count, score
        FROM zones 
        WHERE violation_count < 50
        ORDER BY score DESC LIMIT 10
    """).fetchall()
    
    for row in top_small:
        print(f"Station: {row[0]:<20} | Violations: {row[1]:<6} | Score: {row[2]:.4f}")

if __name__ == "__main__":
    check_outliers()
