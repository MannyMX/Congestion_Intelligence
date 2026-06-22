import numpy as np
from typing import List, Dict, Any
import logging

try:
    from ultralytics import YOLO
    ULTRA_AVAILABLE = True
except ImportError:
    ULTRA_AVAILABLE = False
    logging.warning("Ultralytics not installed. VehicleDetector will not function.")

class VehicleDetector:
    """
    Wraps YOLOv8 to detect vehicles in a single frame.
    Uses pretrained COCO weights. COCO classes for vehicles:
    2: car, 3: motorcycle, 5: bus, 7: truck
    """
    def __init__(self, model_path: str = "yolov8n.pt", confidence_threshold: float = 0.3):
        self.confidence_threshold = confidence_threshold
        # Allowed COCO classes
        self.allowed_classes = {2: 'car', 3: 'motorcycle', 5: 'bus', 7: 'truck'}
        
        if ULTRA_AVAILABLE:
            # Initialize YOLOv8 model. 'yolov8n.pt' will be downloaded automatically if missing.
            self.model = YOLO(model_path)
        else:
            self.model = None

    def detect(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Runs inference on a single frame and returns a list of detections.
        """
        if self.model is None:
            raise RuntimeError("YOLO model is not initialized (ultralytics missing).")

        # Run inference, restricting to vehicle classes
        results = self.model(frame, classes=list(self.allowed_classes.keys()), conf=self.confidence_threshold, verbose=False)
        
        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0].cpu().numpy())
                cls_id = int(box.cls[0].cpu().numpy())
                
                detections.append({
                    "bbox": [float(x1), float(y1), float(x2), float(y2)],
                    "confidence": conf,
                    "class_id": cls_id,
                    "class_name": self.allowed_classes.get(cls_id, "unknown")
                })
                
        return detections
