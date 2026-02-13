from pydantic import BaseModel
from typing import Optional
from enum import Enum


class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class VideoUploadResponse(BaseModel):
    job_id: str
    status: JobStatus
    message: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    progress: float  # 0-100
    message: str
    result_url: Optional[str] = None
    stats_url: Optional[str] = None


class PlayerStats(BaseModel):
    player_id: int
    frames_tracked: int
    distance_covered_px: float
    avg_speed_px_per_frame: float
    zone_coverage: dict  # zone_id -> frame_count
    heatmap_url: Optional[str] = None


class BallStats(BaseModel):
    total_frames_tracked: int
    avg_speed_px_per_frame: float
    max_speed_px_per_frame: float
    trajectories: list  # list of trajectory segments
    serves_detected: int
    spikes_detected: int


class RallyInfo(BaseModel):
    rally_id: int
    start_frame: int
    end_frame: int
    duration_frames: int
    shots: list


class AnalyticsResult(BaseModel):
    job_id: str
    video_duration_sec: float
    total_frames: int
    fps: float
    players: list[PlayerStats]
    ball: BallStats
    rallies: list[RallyInfo]
    zone_heatmap: dict
    annotated_video_url: str
