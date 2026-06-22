import unittest
from src.cv.tracking.tracker import DwellTimeTracker

class TestDwellTracking(unittest.TestCase):
    def setUp(self):
        # 10 second threshold for faster test reasoning
        self.tracker = DwellTimeTracker(dwell_threshold_seconds=10.0, displacement_threshold_pixels=10.0)

    def test_vehicle_stays_still(self):
        # Frame 1: Vehicle appears
        det1 = [{"track_id": 1, "bbox": [100, 100, 120, 120]}]
        res1 = self.tracker.update(frame_timestamp=0.0, detections_with_ids=det1)
        self.assertFalse(res1[0]["is_parked"])
        
        # Frame 2: Vehicle hasn't moved, 5 seconds pass (under threshold)
        det2 = [{"track_id": 1, "bbox": [101, 101, 121, 121]}] # Moved 1 pixel
        res2 = self.tracker.update(frame_timestamp=5.0, detections_with_ids=det2)
        self.assertFalse(res2[0]["is_parked"])
        
        # Frame 3: Vehicle hasn't moved, 11 seconds pass (past threshold)
        det3 = [{"track_id": 1, "bbox": [102, 102, 122, 122]}]
        res3 = self.tracker.update(frame_timestamp=11.0, detections_with_ids=det3)
        self.assertTrue(res3[0]["is_parked"])

    def test_vehicle_moves_continuously(self):
        # Appears
        det1 = [{"track_id": 2, "bbox": [100, 100, 120, 120]}]
        self.tracker.update(0.0, det1)
        
        # Moves 20 pixels (above displacement threshold of 10) at 5 seconds
        det2 = [{"track_id": 2, "bbox": [120, 120, 140, 140]}]
        res2 = self.tracker.update(5.0, det2)
        self.assertFalse(res2[0]["is_parked"])
        self.assertEqual(res2[0]["dwell_time"], 0.0) # Timer reset
        
        # Moves another 20 pixels at 11 seconds
        det3 = [{"track_id": 2, "bbox": [140, 140, 160, 160]}]
        res3 = self.tracker.update(11.0, det3)
        self.assertFalse(res3[0]["is_parked"])
        self.assertEqual(res3[0]["dwell_time"], 0.0) # Timer reset again

    def test_vehicle_stops_just_under_threshold(self):
        # Appears
        det1 = [{"track_id": 3, "bbox": [100, 100, 120, 120]}]
        self.tracker.update(0.0, det1)
        
        # Stays still for 9.9 seconds (threshold is 10.0)
        det2 = [{"track_id": 3, "bbox": [100, 100, 120, 120]}]
        res2 = self.tracker.update(9.9, det2)
        self.assertFalse(res2[0]["is_parked"])

if __name__ == '__main__':
    unittest.main()
