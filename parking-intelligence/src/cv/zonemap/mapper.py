import cv2
import numpy as np
import json
from shapely.geometry import Point, shape
from typing import List, Tuple, Dict, Any

class CameraCalibration:
    """
    Computes a homography matrix from >=4 reference points to map 
    camera pixels (x, y) to GPS coordinates (lon, lat).
    """
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            config = json.load(f)
            
        self.camera_id = config.get("camera_id", "unknown")
        
        src_pts = []
        dst_pts = []
        for pt in config.get("reference_points", []):
            src_pts.append([pt["pixel_x"], pt["pixel_y"]])
            dst_pts.append([pt["lon"], pt["lat"]])
            
        if len(src_pts) < 4:
            raise ValueError(f"Need at least 4 reference points, got {len(src_pts)}")
            
        self.homography, _ = cv2.findHomography(
            np.array(src_pts, dtype=np.float32), 
            np.array(dst_pts, dtype=np.float32)
        )

    def pixel_to_gps(self, pixel_x: float, pixel_y: float) -> Tuple[float, float]:
        if self.homography is None:
            raise ValueError("Homography matrix not computed")
            
        # Homogeneous coordinates
        pt = np.array([[[pixel_x, pixel_y]]], dtype=np.float32)
        gps_pt = cv2.perspectiveTransform(pt, self.homography)
        return float(gps_pt[0][0][0]), float(gps_pt[0][0][1]) # lon, lat

class ZoneMapper:
    """
    Tests GPS points against existing Stage 1 GeoJSON zone polygons.
    Does NOT invent new zones, only maps to existing ones.
    """
    def __init__(self, zones_geojson: List[Dict[str, Any]]):
        self.zones = []
        for zone in zones_geojson:
            # Reconstruct Shapely geometry from geojson
            if 'geojson' in zone:
                geom = shape(zone['geojson'])
                self.zones.append({
                    "zone_id": zone["zone_id"],
                    "polygon": geom
                })

    def get_zone_for_gps(self, lon: float, lat: float) -> int:
        """
        Returns zone_id if the point is inside a zone, otherwise None.
        """
        pt = Point(lon, lat)
        for zone in self.zones:
            if zone["polygon"].contains(pt):
                return zone["zone_id"]
        return None
