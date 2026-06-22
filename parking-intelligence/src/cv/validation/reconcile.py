import duckdb
import os
import pandas as pd
from typing import List, Dict, Any
import logging

class ReconciliationReport:
    """
    Sanity-check tool comparing synthetic live detection events against 
    Stage 1 historical baseline counts per zone.
    """
    def __init__(self, db_path: str = "data/processed/parking_intelligence.duckdb"):
        self.db_path = db_path

    def run_report(self, synthetic_live_events: List[Dict[str, Any]]):
        logging.warning("=== RECONCILIATION REPORT (SYNTHETIC FIXTURES ONLY) ===")
        logging.warning("These numbers are based on synthetic test fixtures, NOT real camera data.")
        
        if not os.path.exists(self.db_path):
            logging.error(f"DuckDB database not found at {self.db_path}")
            return
            
        conn = duckdb.connect(self.db_path)
        
        # Aggregate synthetic live events
        live_counts = {}
        for event in synthetic_live_events:
            if not event.get("is_parked"):
                continue
            zid = event.get("zone_id")
            if zid is not None:
                live_counts[zid] = live_counts.get(zid, 0) + 1
                
        # Fetch historical counts
        historical = conn.execute("SELECT zone_id, violation_count FROM zones").df()
        
        print("\nZONE ID | HISTORICAL | SYNTHETIC LIVE | DISCREPANCY FLAG")
        print("-" * 60)
        
        for _, row in historical.iterrows():
            zid = int(row['zone_id'])
            hist_count = int(row['violation_count'])
            live_count = live_counts.get(zid, 0)
            
            flag = ""
            if live_count > hist_count:
                flag = "WARNING: Live exceeds 6-month historical"
            elif live_count > 0:
                flag = "INFO: Active synthetic detections"
                
            if live_count > 0 or hist_count > 10000: # Show active zones or huge hotspots
                print(f"{zid:<7} | {hist_count:<10} | {live_count:<14} | {flag}")
                
        print("-" * 60)
        logging.warning("=== END SYNTHETIC REPORT ===")
