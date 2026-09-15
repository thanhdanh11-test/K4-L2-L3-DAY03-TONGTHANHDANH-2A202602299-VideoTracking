#!/usr/bin/env python3
"""Metrics and evaluation calculation module."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path


def analyze_tracks(tracked_frames: list[dict]) -> dict:
    """Analyze track lifespan, frequency, and statistics."""
    track_history = defaultdict(list)
    total_boxes = 0

    for frame in tracked_frames:
        f_idx = frame["frame_idx"]
        for det in frame["detections"]:
            tid = det["track_id"]
            track_history[tid].append({
                "frame": f_idx,
                "box": det["box"],
                "conf": det["conf"],
                "cls": det.get("cls", "car")
            })
            total_boxes += 1

    tracks_summary = {}
    for tid, instances in track_history.items():
        frames = [i["frame"] for i in instances]
        confs = [i["conf"] for i in instances]
        tracks_summary[tid] = {
            "first_frame": min(frames),
            "last_frame": max(frames),
            "duration_frames": len(frames),
            "lifespan_span": max(frames) - min(frames) + 1,
            "avg_confidence": round(sum(confs) / len(confs), 3),
            "class": instances[0]["cls"],
        }

    return {
        "total_frames_processed": len(tracked_frames),
        "total_detections": total_boxes,
        "unique_track_count": len(tracks_summary),
        "tracks": tracks_summary,
    }
