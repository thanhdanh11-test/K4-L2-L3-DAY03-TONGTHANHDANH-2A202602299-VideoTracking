#!/usr/bin/env python3
"""Visualization module for rendering tracking video and visual summary grids."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import cv2
import numpy as np

# High-contrast color palette for stable track identity
PALETTE = [
    (0, 240, 255),    # Cyan
    (50, 255, 120),   # Neon Green
    (255, 90, 95),    # Coral
    (255, 215, 0),    # Gold
    (180, 105, 255),  # Violet
    (255, 110, 199),  # Pink
    (0, 180, 255),    # Azure
    (255, 165, 0),    # Orange
]


def get_color(track_id: int) -> tuple[int, int, int]:
    rgb = PALETTE[(track_id - 1) % len(PALETTE)]
    return (rgb[2], rgb[1], rgb[0])  # BGR for OpenCV


class TrackingVisualizer:
    def __init__(self, fps: float = 12.5):
        self.fps = fps
        self.trajectories = defaultdict(list)

    def draw_frame(self, image: np.ndarray, frame_idx: int, total_frames: int, detections: list[dict]) -> np.ndarray:
        frame = image.copy()
        h, w = frame.shape[:2]

        # Update trajectories
        for det in detections:
            tid = det["track_id"]
            x, y, bw, bh = det["box"]
            cx = int(x + bw / 2)
            cy = int(y + bh / 2)
            self.trajectories[tid].append((cx, cy))
            if len(self.trajectories[tid]) > 25:
                self.trajectories[tid].pop(0)

        # 1. Draw trajectory trails
        for tid, points in self.trajectories.items():
            if len(points) >= 2:
                bgr = get_color(tid)
                for i in range(1, len(points)):
                    alpha = i / len(points)
                    thickness = max(1, int(3 * alpha))
                    cv2.line(frame, points[i - 1], points[i], bgr, thickness, cv2.LINE_AA)

        # 2. Draw boxes and badges
        for det in detections:
            tid = det["track_id"]
            x, y, bw, bh = det["box"]
            x1, y1 = int(round(x)), int(round(y))
            x2, y2 = int(round(x + bw)), int(round(y + bh))
            bgr = get_color(tid)

            # Box outline with corner accents
            cv2.rectangle(frame, (x1, y1), (x2, y2), bgr, 2, cv2.LINE_AA)
            c_len = min(12, int(min(bw, bh) * 0.25))
            if c_len > 3:
                cv2.line(frame, (x1, y1), (x1 + c_len, y1), (255, 255, 255), 2, cv2.LINE_AA)
                cv2.line(frame, (x1, y1), (x1, y1 + c_len), (255, 255, 255), 2, cv2.LINE_AA)
                cv2.line(frame, (x2, y2), (x2 - c_len, y2), (255, 255, 255), 2, cv2.LINE_AA)
                cv2.line(frame, (x2, y2), (x2, y2 - c_len), (255, 255, 255), 2, cv2.LINE_AA)

            # Badge
            label = f"ID:{tid} {det.get('cls', 'car').upper()} ({det['conf']:.2f})"
            font = cv2.FONT_HERSHEY_SIMPLEX
            (tw, th), bl = cv2.getTextSize(label, font, 0.45, 1)
            by1 = max(0, y1 - th - 8)
            by2 = by1 + th + 8
            bx2 = min(w, x1 + tw + 8)
            cv2.rectangle(frame, (x1, by1), (bx2, by2), bgr, -1)
            cv2.putText(frame, label, (x1 + 4, by2 - bl - 2), font, 0.45, (10, 10, 10), 1, cv2.LINE_AA)

        # 3. Top HUD Bar
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 38), (15, 18, 24), -1)
        cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)
        cv2.line(frame, (0, 38), (w, 38), (0, 240, 255), 1)

        hud_left = "GEMINI TRACKING ENGINE · AI TEST"
        hud_right = f"Frame {frame_idx:03d}/{total_frames:03d} | Active: {len(detections)} cars"
        cv2.putText(frame, hud_left, (14, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 240, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, hud_right, (w - 320, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (230, 230, 230), 1, cv2.LINE_AA)

        return frame

    def render_video(self, tracked_frames: list[dict], output_video: Path | str) -> None:
        out_path = Path(output_video)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        total = len(tracked_frames)
        if total == 0:
            return

        first_img = cv2.imread(str(tracked_frames[0]["image_path"]))
        h, w = first_img.shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(str(out_path), fourcc, self.fps, (w, h))

        self.trajectories.clear()
        for item in tracked_frames:
            raw = cv2.imread(str(item["image_path"]))
            drawn = self.draw_frame(raw, item["frame_idx"], total, item["detections"])
            writer.write(drawn)

        writer.release()
        print(f"  Đã xuất video tracking: {out_path} ({out_path.stat().st_size / 1024 / 1024:.2f} MB)")

    def render_grid_summary(self, tracked_frames: list[dict], output_img: Path | str, frame_indices: list[int]) -> None:
        """Render a 2x2 collage of selected frames for quick inspection."""
        out_path = Path(output_img)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        frames_by_idx = {f["frame_idx"]: f for f in tracked_frames}
        selected = []
        total = len(tracked_frames)

        for f_idx in frame_indices:
            item = frames_by_idx.get(f_idx)
            if item:
                raw = cv2.imread(str(item["image_path"]))
                drawn = self.draw_frame(raw, item["frame_idx"], total, item["detections"])
                # Resize to half
                h, w = drawn.shape[:2]
                half = cv2.resize(drawn, (w // 2, h // 2), interpolation=cv2.INTER_AREA)
                selected.append(half)

        if len(selected) == 4:
            top_row = np.hstack([selected[0], selected[1]])
            bot_row = np.hstack([selected[2], selected[3]])
            grid = np.vstack([top_row, bot_row])
            cv2.imwrite(str(out_path), grid, [cv2.IMWRITE_JPEG_QUALITY, 92])
            print(f"  Đã xuất ảnh tổng hợp tracking collage: {out_path}")
