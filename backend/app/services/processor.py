"""
Video processing pipeline: detect → track → analyze → annotate.
"""

import cv2
import numpy as np
import supervision as sv
import json
import asyncio
import logging
from pathlib import Path

from .detector import VolleyballDetector
from .tracker import VolleyballTracker
from .analytics import VolleyballAnalytics
from ..database import update_job

logger = logging.getLogger(__name__)

OUTPUT_DIR = Path("data/output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


async def process_video(job_id: str, video_path: str):
    """Main processing pipeline — runs in background."""
    try:
        await update_job(job_id, status="processing", progress=0, message="Initializing...")

        # Init components
        detector = VolleyballDetector()
        tracker = VolleyballTracker()

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            await update_job(job_id, status="failed", message="Cannot open video file")
            return

        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        analytics = VolleyballAnalytics(width, height, fps)

        # Output video
        out_path = OUTPUT_DIR / f"{job_id}_annotated.mp4"
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(str(out_path), fourcc, fps, (width, height))

        # Annotators
        box_annotator = sv.BoxAnnotator(thickness=2)
        label_annotator = sv.LabelAnnotator(text_scale=0.5)
        trace_annotator = sv.TraceAnnotator(thickness=2, trace_length=30)

        await update_job(job_id, progress=5, message="Processing frames...")

        frame_idx = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Detect
            detections = detector.detect(frame)

            # Track
            player_dets, ball_dets = tracker.update(detections)

            # Analytics
            analytics.process_frame(frame_idx, player_dets, ball_dets)

            # Annotate
            annotated = frame.copy()

            if len(player_dets) > 0:
                labels_p = [
                    f"P{tid}" if tid is not None else "P?"
                    for tid in (player_dets.tracker_id if player_dets.tracker_id is not None else [])
                ]
                annotated = box_annotator.annotate(annotated, player_dets)
                if labels_p:
                    annotated = label_annotator.annotate(annotated, player_dets, labels=labels_p)
                annotated = trace_annotator.annotate(annotated, player_dets)

            if len(ball_dets) > 0:
                annotated = box_annotator.annotate(annotated, ball_dets)
                annotated = trace_annotator.annotate(annotated, ball_dets)

            writer.write(annotated)
            frame_idx += 1

            # Update progress every 30 frames
            if frame_idx % 30 == 0:
                pct = min(95, 5 + (frame_idx / max(total_frames, 1)) * 90)
                await update_job(job_id, progress=round(pct, 1),
                                 message=f"Frame {frame_idx}/{total_frames}")

        cap.release()
        writer.release()

        # Generate results
        results = analytics.get_results()
        results["video_duration_sec"] = round(total_frames / fps, 2) if fps > 0 else 0

        stats_path = OUTPUT_DIR / f"{job_id}_stats.json"
        with open(stats_path, "w") as f:
            json.dump(results, f, indent=2)

        await update_job(
            job_id,
            status="completed",
            progress=100,
            message="Processing complete",
            annotated_video_path=str(out_path),
            stats_json=json.dumps(results),
        )
        logger.info(f"Job {job_id} completed: {frame_idx} frames processed")

    except Exception as e:
        logger.exception(f"Job {job_id} failed")
        await update_job(job_id, status="failed", message=str(e))
