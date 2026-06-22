from fastapi import APIRouter, Depends, HTTPException
from src.data.dao import ParkingDAO
import json
import os

router = APIRouter()

def get_dao():
    db_path = os.environ.get("DUCKDB_PATH", "data/processed/parking_intelligence.duckdb")
    dao = ParkingDAO(db_path=db_path)
    try:
        yield dao
    finally:
        dao.close()

@router.get("/zones")
def get_ranked_zones(limit: int = 50, dao: ParkingDAO = Depends(get_dao)):
    try:
        df = dao.get_top_zones(limit=limit)
        zones = []
        for _, row in df.iterrows():
            zone_data = row.to_dict()
            if isinstance(zone_data['geojson'], str):
                zone_data['geojson'] = json.loads(zone_data['geojson'])
            if isinstance(zone_data['score_breakdown'], str):
                zone_data['score_breakdown'] = json.loads(zone_data['score_breakdown'])
            zones.append(zone_data)
        return {"data": zones}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/heatmap")
def get_heatmap_data(dao: ParkingDAO = Depends(get_dao)):
    try:
        df = dao.get_all_violations()
        points = df[['latitude', 'longitude']].dropna().values.tolist()
        return {"data": points}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
