import duckdb
import pandas as pd
import geopandas as gpd
from pathlib import Path

# Explicitly ensure pyogrio is used if any internal I/O happens in geopandas
gpd.options.io_engine = "pyogrio"

class ParkingDAO:
    def __init__(self, db_path: str = "data/processed/parking_intelligence.duckdb"):
        self.db_path = db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = duckdb.connect(self.db_path)
        self.conn.install_extension("spatial")
        self.conn.load_extension("spatial")
        self._init_tables()

    def _init_tables(self):
        self.conn.execute("""
            CREATE SEQUENCE IF NOT EXISTS seq_zone_id;
            CREATE TABLE IF NOT EXISTS zones (
                zone_id INTEGER DEFAULT nextval('seq_zone_id'),
                centroid_lat DOUBLE,
                centroid_lon DOUBLE,
                violation_count INTEGER,
                dominant_vehicle_type VARCHAR,
                dominant_violation_tag VARCHAR,
                police_station VARCHAR,
                geom GEOMETRY,
                score DOUBLE,
                score_breakdown JSON
            );
        """)
        
    def save_zones(self, zones_gdf: gpd.GeoDataFrame):
        """Saves zones to the duckdb spatial table."""
        self.conn.execute("DELETE FROM zones;")
        
        df = zones_gdf.copy()
        df['geom'] = df['geometry'].apply(lambda x: x.wkt)
        df = df.drop(columns=['geometry'])
        
        self.conn.register('temp_zones_view', df)
        self.conn.execute("""
            INSERT INTO zones (
                centroid_lat, centroid_lon, violation_count, 
                dominant_vehicle_type, dominant_violation_tag, 
                police_station, geom, score, score_breakdown
            )
            SELECT 
                centroid_lat, centroid_lon, violation_count,
                dominant_vehicle_type, dominant_violation_tag,
                police_station, ST_GeomFromText(geom), score, score_breakdown
            FROM temp_zones_view
        """)
        self.conn.unregister('temp_zones_view')

    def save_violations(self, df: pd.DataFrame):
        self.conn.register('temp_violations', df)
        self.conn.execute("CREATE OR REPLACE TABLE historical_violation_events AS SELECT * FROM temp_violations")
        self.conn.unregister('temp_violations')
        
    def get_top_zones(self, limit: int = 50) -> pd.DataFrame:
        return self.conn.execute(f"""
            SELECT zone_id, centroid_lat, centroid_lon, violation_count, 
                   dominant_vehicle_type, dominant_violation_tag, police_station,
                   ST_AsGeoJSON(geom) as geojson, score, score_breakdown
            FROM zones
            ORDER BY score DESC
            LIMIT {limit}
        """).df()

    def get_all_violations(self) -> pd.DataFrame:
        return self.conn.execute("SELECT * FROM historical_violation_events").df()

    def close(self):
        self.conn.close()
