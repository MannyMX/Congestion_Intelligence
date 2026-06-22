import time
import math
from typing import Dict, Any, List

class DwellTimeTracker:
    """
    Maintains position history for tracked object IDs and classifies them as "parked"
    if their bounding-box centroid displacement remains under a threshold for longer 
    than dwell_threshold_seconds.
    """
    def __init__(self, dwell_threshold_seconds: float = 90.0, displacement_threshold_pixels: float = 20.0):
        self.dwell_threshold = dwell_threshold_seconds
        self.displacement_threshold = displacement_threshold_pixels
        # Stores track state: { track_id: {"first_seen": timestamp, "last_seen": timestamp, "centroid": (x,y), "parked": bool} }
        self.tracks: Dict[int, Dict[str, Any]] = {}

    def update(self, frame_timestamp: float, detections_with_ids: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Updates tracking state with new detections (which must have 'track_id' from ByteTrack).
        Returns the list of detections, with a new boolean field 'is_parked'.
        """
        current_frame_tracks = set()
        
        for det in detections_with_ids:
            track_id = det.get("track_id")
            if track_id is None:
                continue
                
            current_frame_tracks.add(track_id)
            bbox = det["bbox"]
            centroid_x = (bbox[0] + bbox[2]) / 2.0
            centroid_y = (bbox[1] + bbox[3]) / 2.0
            
            if track_id not in self.tracks:
                # New track
                self.tracks[track_id] = {
                    "first_seen": frame_timestamp,
                    "last_seen": frame_timestamp,
                    "centroid": (centroid_x, centroid_y),
                    "parked": False
                }
            else:
                # Existing track - check displacement
                state = self.tracks[track_id]
                old_x, old_y = state["centroid"]
                displacement = math.sqrt((centroid_x - old_x)**2 + (centroid_y - old_y)**2)
                
                if displacement > self.displacement_threshold:
                    # Vehicle moved significantly, reset its dwell timer
                    state["first_seen"] = frame_timestamp
                    state["centroid"] = (centroid_x, centroid_y)
                    state["parked"] = False
                else:
                    # Vehicle is stationary
                    dwell_time = frame_timestamp - state["first_seen"]
                    if dwell_time >= self.dwell_threshold:
                        state["parked"] = True
                        
                state["last_seen"] = frame_timestamp
                
            det["is_parked"] = self.tracks[track_id]["parked"]
            det["dwell_time"] = frame_timestamp - self.tracks[track_id]["first_seen"]

        # Clean up stale tracks (not seen in last 5 minutes)
        stale_threshold = 300.0
        stale_ids = [tid for tid, state in self.tracks.items() if (frame_timestamp - state["last_seen"]) > stale_threshold]
        for tid in stale_ids:
            del self.tracks[tid]
            
        return detections_with_ids
