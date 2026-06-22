import cv2
import numpy as np
import os
import unittest
from src.cv.detection.sampler import FrameSampler
from src.cv.detection.detector import VehicleDetector

class TestDetection(unittest.TestCase):
    def setUp(self):
        self.fixture_dir = "tests/fixtures"
        os.makedirs(self.fixture_dir, exist_ok=True)
        self.dummy_video = os.path.join(self.fixture_dir, "dummy.mp4")
        
        # Create a dummy video with 10 frames at 10 fps
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(self.dummy_video, fourcc, 10.0, (640, 480))
        for i in range(10):
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            # Draw a simulated vehicle (white rectangle)
            cv2.rectangle(frame, (100, 100), (200, 200), (255, 255, 255), -1)
            out.write(frame)
        out.release()
        
    def test_frame_sampler(self):
        # Sample at 2 FPS from a 10 FPS video. Should yield ~2 frames from 1 sec of video
        sampler = FrameSampler(self.dummy_video, target_fps=2.0)
        frames = list(sampler.sample())
        # The video is 10 frames @ 10fps = 1 second long
        # At 2 fps, we expect 2 frames (maybe 3 depending on exact interval boundary)
        self.assertTrue(len(frames) in [2, 3])
        self.assertEqual(frames[0].shape, (480, 640, 3))

    def test_vehicle_detector_mocked(self):
        # We test the wrapper logic. Since we don't want to download YOLO weights 
        # in a strict isolated test run unless intended, we mock the model response
        # or we run YOLO but expect nothing if weights aren't downloaded.
        # Given it's a scaffold, we will just test instantiation and interface.
        detector = VehicleDetector(model_path="yolov8n.pt", confidence_threshold=0.3)
        
        # Create a blank frame
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # In a real environment, this might download weights once. 
        # For synthetic test, we just ensure it doesn't crash.
        detections = detector.detect(frame)
        
        # Blank frame should yield 0 vehicle detections
        self.assertEqual(len(detections), 0)

    def tearDown(self):
        if os.path.exists(self.dummy_video):
            os.remove(self.dummy_video)

if __name__ == '__main__':
    unittest.main()
