"""
Multi-object tracking using ByteTrack via the trackers library.
"""

import numpy as np
import supervision as sv
from trackers import ByteTrack
import logging

logger = logging.getLogger(__name__)


class VolleyballTracker:
    def __init__(self):
        self.player_tracker = ByteTrack()
        self.ball_tracker = ByteTrack(
            minimum_consecutive_frames=1,  # ball can disappear briefly
        )

    def update(self, detections: sv.Detections) -> tuple[sv.Detections, sv.Detections]:
        """
        Split detections into players and ball, track each separately.
        Returns (player_detections, ball_detections) with tracker_id assigned.
        """
        if detections.class_id is None or len(detections) == 0:
            return sv.Detections.empty(), sv.Detections.empty()

        # Split by class: 0=ball, 1=player
        ball_mask = detections.class_id == 0
        player_mask = detections.class_id == 1

        ball_dets = detections[ball_mask]
        player_dets = detections[player_mask]

        # Track
        tracked_players = self._track(self.player_tracker, player_dets)
        tracked_balls = self._track(self.ball_tracker, ball_dets)

        return tracked_players, tracked_balls

    def _track(self, tracker: ByteTrack, detections: sv.Detections) -> sv.Detections:
        if len(detections) == 0:
            return detections
        try:
            tracked = tracker.update(detections=detections)
            return tracked
        except Exception as e:
            logger.error(f"Tracking error: {e}")
            return detections
