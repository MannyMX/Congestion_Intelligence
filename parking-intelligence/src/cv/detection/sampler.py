import cv2
import numpy as np
import time

class FrameSampler:
    """
    Yields frames from a video source at a configurable rate to limit compute.
    """
    def __init__(self, source: str, target_fps: float = 2.0):
        self.source = source
        self.target_fps = target_fps
        self.interval = 1.0 / target_fps
        
    def sample(self):
        cap = cv2.VideoCapture(self.source)
        if not cap.isOpened():
            raise RuntimeError(f"Could not open source {self.source}")
            
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0: fps = 30.0
            
        last_yield_time = -self.interval # Ensure first frame is yielded
        frame_idx = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            current_time = frame_idx / fps
            
            if current_time - last_yield_time >= self.interval:
                yield frame
                last_yield_time = current_time
                
            frame_idx += 1
                
        cap.release()
