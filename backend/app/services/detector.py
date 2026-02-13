"""
Detection service — tries Roboflow inference first, falls back to YOLO.
Uses FREE tier only (no API key required for public models).
"""

import numpy as np
import supervision as sv
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Class mappings for volleyball detection
VOLLEYBALL_CLASSES = {
    "volleyball": 0,
    "ball": 0,
    "player": 1,
    "person": 1,
    "net": 2,
}


class VolleyballDetector:
    def __init__(self):
        self.model = None
        self.model_type = None
        self._init_model()

    def _init_model(self):
        """Try Roboflow inference first, then YOLO fallback."""
        # Try 1: Roboflow inference with public volleyball model
        try:
            from inference import get_model
            self.model = get_model(model_id="volleyball-tracking/2")
            self.model_type = "roboflow"
            logger.info("Loaded Roboflow volleyball-tracking model")
            return
        except Exception as e:
            logger.warning(f"Roboflow model failed: {e}")

        # Try 2: YOLO (ultralytics) — detect persons + sports ball
        try:
            from ultralytics import YOLO
            self.model = YOLO("yolov8n.pt")  # nano model, free
            self.model_type = "yolo"
            logger.info("Loaded YOLOv8 nano as fallback")
            return
        except Exception as e:
            logger.warning(f"YOLO failed: {e}")

        logger.error("No detection model available!")

    def detect(self, frame: np.ndarray) -> sv.Detections:
        """Run detection on a single frame, return sv.Detections."""
        if self.model is None:
            return sv.Detections.empty()

        if self.model_type == "roboflow":
            return self._detect_roboflow(frame)
        elif self.model_type == "yolo":
            return self._detect_yolo(frame)
        return sv.Detections.empty()

    def _detect_roboflow(self, frame: np.ndarray) -> sv.Detections:
        try:
            result = self.model.infer(frame)[0]
            return sv.Detections.from_inference(result)
        except Exception as e:
            logger.error(f"Roboflow detection error: {e}")
            return sv.Detections.empty()

    def _detect_yolo(self, frame: np.ndarray) -> sv.Detections:
        try:
            results = self.model(frame, verbose=False)[0]
            detections = sv.Detections.from_ultralytics(results)

            # Filter to persons (class 0) and sports balls (class 32)
            mask = np.isin(detections.class_id, [0, 32])
            filtered = detections[mask]

            # Remap: person(0)->1(player), sports_ball(32)->0(ball)
            if filtered.class_id is not None and len(filtered.class_id) > 0:
                new_ids = np.where(filtered.class_id == 0, 1, 0)
                filtered.class_id = new_ids

            return filtered
        except Exception as e:
            logger.error(f"YOLO detection error: {e}")
            return sv.Detections.empty()
