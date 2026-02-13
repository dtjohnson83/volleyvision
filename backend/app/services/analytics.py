"""
Volleyball-specific analytics: player movement, ball trajectory,
rally detection, shot classification, court zone mapping.
"""

import numpy as np
from collections import defaultdict
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)

# Court zones (3x3 grid on each side = 18 zones total)
# Zones 1-9: near side, Zones 10-18: far side
ZONE_COLS = 3
ZONE_ROWS = 3


@dataclass
class FrameData:
    frame_idx: int
    player_positions: dict  # tracker_id -> (cx, cy)
    ball_position: tuple | None  # (cx, cy) or None


@dataclass
class PlayerTrack:
    player_id: int
    positions: list = field(default_factory=list)  # [(frame, x, y), ...]
    zone_visits: dict = field(default_factory=lambda: defaultdict(int))

    @property
    def distance_covered(self) -> float:
        if len(self.positions) < 2:
            return 0.0
        total = 0.0
        for i in range(1, len(self.positions)):
            dx = self.positions[i][1] - self.positions[i - 1][1]
            dy = self.positions[i][2] - self.positions[i - 1][2]
            total += np.sqrt(dx ** 2 + dy ** 2)
        return total

    @property
    def avg_speed(self) -> float:
        if len(self.positions) < 2:
            return 0.0
        return self.distance_covered / len(self.positions)


@dataclass
class BallTrack:
    positions: list = field(default_factory=list)  # [(frame, x, y), ...]
    speeds: list = field(default_factory=list)

    def add(self, frame: int, x: float, y: float):
        if self.positions:
            last = self.positions[-1]
            dx = x - last[1]
            dy = y - last[2]
            speed = np.sqrt(dx ** 2 + dy ** 2)
            self.speeds.append(speed)
        self.positions.append((frame, x, y))


class VolleyballAnalytics:
    def __init__(self, frame_width: int, frame_height: int, fps: float):
        self.width = frame_width
        self.height = frame_height
        self.fps = fps
        self.players: dict[int, PlayerTrack] = {}
        self.ball = BallTrack()
        self.frames: list[FrameData] = []
        self.rallies: list[dict] = []

        # For rally detection
        self._ball_visible_streak = 0
        self._ball_missing_streak = 0
        self._rally_start_frame = None
        self._in_rally = False

    def get_zone(self, x: float, y: float) -> int:
        """Map pixel position to zone (1-9)."""
        col = min(int(x / self.width * ZONE_COLS), ZONE_COLS - 1)
        row = min(int(y / self.height * ZONE_ROWS), ZONE_ROWS - 1)
        return row * ZONE_COLS + col + 1

    def process_frame(self, frame_idx: int, player_dets, ball_dets):
        """Process one frame of detections."""
        player_positions = {}
        ball_position = None

        # Players
        if hasattr(player_dets, 'tracker_id') and player_dets.tracker_id is not None:
            for i, tid in enumerate(player_dets.tracker_id):
                bbox = player_dets.xyxy[i]
                cx = (bbox[0] + bbox[2]) / 2
                cy = (bbox[1] + bbox[3]) / 2
                tid = int(tid)

                if tid not in self.players:
                    self.players[tid] = PlayerTrack(player_id=tid)

                self.players[tid].positions.append((frame_idx, cx, cy))
                zone = self.get_zone(cx, cy)
                self.players[tid].zone_visits[zone] += 1
                player_positions[tid] = (cx, cy)

        # Ball
        if len(ball_dets) > 0:
            bbox = ball_dets.xyxy[0]
            cx = (bbox[0] + bbox[2]) / 2
            cy = (bbox[1] + bbox[3]) / 2
            self.ball.add(frame_idx, cx, cy)
            ball_position = (cx, cy)
            self._ball_visible_streak += 1
            self._ball_missing_streak = 0
        else:
            self._ball_visible_streak = 0
            self._ball_missing_streak += 1

        # Rally detection
        self._detect_rally(frame_idx)

        self.frames.append(FrameData(
            frame_idx=frame_idx,
            player_positions=player_positions,
            ball_position=ball_position,
        ))

    def _detect_rally(self, frame_idx: int):
        """Simple rally detection: ball visible = rally in progress."""
        rally_start_threshold = int(self.fps * 0.5)  # ball visible 0.5s
        rally_end_threshold = int(self.fps * 2)  # ball missing 2s

        if not self._in_rally and self._ball_visible_streak >= rally_start_threshold:
            self._in_rally = True
            self._rally_start_frame = frame_idx - self._ball_visible_streak

        if self._in_rally and self._ball_missing_streak >= rally_end_threshold:
            self._in_rally = False
            self.rallies.append({
                "rally_id": len(self.rallies) + 1,
                "start_frame": self._rally_start_frame,
                "end_frame": frame_idx - self._ball_missing_streak,
                "duration_frames": (frame_idx - self._ball_missing_streak) - self._rally_start_frame,
            })

    def classify_shots(self) -> dict:
        """Classify shots based on ball trajectory and speed."""
        serves = 0
        spikes = 0
        blocks = 0
        digs = 0

        if len(self.ball.speeds) < 3:
            return {"serves": 0, "spikes": 0, "blocks": 0, "digs": 0}

        speeds = np.array(self.ball.speeds)
        positions = self.ball.positions

        for i in range(2, len(positions)):
            speed = speeds[i - 1] if i - 1 < len(speeds) else 0
            _, x, y = positions[i]
            _, px, py = positions[i - 1]
            dy = y - py  # positive = downward

            high_speed = speed > np.percentile(speeds, 80)
            # Ball moving down fast from top = spike
            if high_speed and dy > 0 and y < self.height * 0.5:
                spikes += 1
            # Ball moving up from bottom = dig
            elif dy < -5 and y > self.height * 0.6:
                digs += 1
            # High speed from back court = serve
            elif high_speed and (y > self.height * 0.7 or y < self.height * 0.3):
                serves += 1

        return {"serves": serves, "spikes": spikes, "blocks": blocks, "digs": digs}

    def generate_heatmap_data(self) -> dict:
        """Generate zone-based heatmap data."""
        zone_counts = defaultdict(int)
        for frame in self.frames:
            for tid, (x, y) in frame.player_positions.items():
                zone = self.get_zone(x, y)
                zone_counts[zone] += 1
            if frame.ball_position:
                bx, by = frame.ball_position
                zone = self.get_zone(bx, by)
                zone_counts[f"ball_{zone}"] += 1
        return dict(zone_counts)

    def get_results(self) -> dict:
        """Compile all analytics into a result dict."""
        shots = self.classify_shots()

        # Close any open rally
        if self._in_rally and self.frames:
            self.rallies.append({
                "rally_id": len(self.rallies) + 1,
                "start_frame": self._rally_start_frame,
                "end_frame": self.frames[-1].frame_idx,
                "duration_frames": self.frames[-1].frame_idx - self._rally_start_frame,
            })

        player_stats = []
        for pid, pt in self.players.items():
            player_stats.append({
                "player_id": pid,
                "frames_tracked": len(pt.positions),
                "distance_covered_px": round(pt.distance_covered, 2),
                "avg_speed_px_per_frame": round(pt.avg_speed, 2),
                "zone_coverage": dict(pt.zone_visits),
            })

        ball_speeds = self.ball.speeds if self.ball.speeds else [0]

        return {
            "total_frames": len(self.frames),
            "fps": self.fps,
            "players": player_stats,
            "ball": {
                "total_frames_tracked": len(self.ball.positions),
                "avg_speed_px_per_frame": round(float(np.mean(ball_speeds)), 2),
                "max_speed_px_per_frame": round(float(np.max(ball_speeds)), 2),
                "serves_detected": shots["serves"],
                "spikes_detected": shots["spikes"],
                "blocks_detected": shots["blocks"],
                "digs_detected": shots["digs"],
            },
            "rallies": [
                {
                    **r,
                    "duration_sec": round(r["duration_frames"] / self.fps, 2) if self.fps > 0 else 0,
                }
                for r in self.rallies
            ],
            "zone_heatmap": self.generate_heatmap_data(),
        }
