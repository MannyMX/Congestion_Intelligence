import unittest
import os
import json
import numpy as np
from shapely.geometry import Polygon, mapping
from src.cv.zonemap.mapper import CameraCalibration, ZoneMapper

class TestZonemap(unittest.TestCase):
    def setUp(self):
        self.config_dir = "config/camera_calibration"
        os.makedirs(self.config_dir, exist_ok=True)
        self.config_path = os.path.join(self.config_dir, "cam_test.json")
        
        # Create a simple synthetic 1:1 mapping config for homography
        # Pixel space is (0,0) to (100,100). GPS space is (10.0, 20.0) to (11.0, 21.0)
        # Shift is +10.0 in lon, +20.0 in lat. Scale is 0.01 per pixel.
        config = {
            "camera_id": "test_cam",
            "reference_points": [
                {"pixel_x": 0, "pixel_y": 0, "lon": 10.0, "lat": 20.0},
                {"pixel_x": 100, "pixel_y": 0, "lon": 11.0, "lat": 20.0},
                {"pixel_x": 100, "pixel_y": 100, "lon": 11.0, "lat": 21.0},
                {"pixel_x": 0, "pixel_y": 100, "lon": 10.0, "lat": 21.0}
            ]
        }
        with open(self.config_path, "w") as f:
            json.dump(config, f)
            
        # Create a mock Stage 1 zone
        # A polygon from (10.4, 20.4) to (10.6, 20.6)
        poly = Polygon([(10.4, 20.4), (10.6, 20.4), (10.6, 20.6), (10.4, 20.6)])
        self.mock_zones = [
            {"zone_id": 99, "geojson": mapping(poly)}
        ]

    def test_homography_correctness(self):
        calib = CameraCalibration(self.config_path)
        
        # Test a known reference point
        lon, lat = calib.pixel_to_gps(0, 0)
        self.assertAlmostEqual(lon, 10.0, places=4)
        self.assertAlmostEqual(lat, 20.0, places=4)
        
        # Test a mid-point
        lon, lat = calib.pixel_to_gps(50, 50)
        self.assertAlmostEqual(lon, 10.5, places=4)
        self.assertAlmostEqual(lat, 20.5, places=4)

    def test_point_in_polygon(self):
        mapper = ZoneMapper(self.mock_zones)
        
        # Point inside
        zone_id = mapper.get_zone_for_gps(10.5, 20.5)
        self.assertEqual(zone_id, 99)
        
        # Point outside
        zone_id = mapper.get_zone_for_gps(10.1, 20.1)
        self.assertIsNone(zone_id)

    def tearDown(self):
        if os.path.exists(self.config_path):
            os.remove(self.config_path)

if __name__ == '__main__':
    unittest.main()
