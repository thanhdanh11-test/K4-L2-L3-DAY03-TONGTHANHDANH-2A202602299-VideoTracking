#!/usr/bin/env python3
"""Run Tracking Test Experiment."""

from __future__ import annotations

import json
import time
from pathlib import Path
import sys

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.tracker import VisualTracker
from src.visualizer import TrackingVisualizer
from src.metrics import analyze_tracks


def main():
    print("=" * 70)
    print("       GEMINI VISUAL TRACKING TEST SUITE (AIVIN LAB)")
    print("=" * 70)

    config_path = PROJECT_ROOT / "configs" / "tracker_config.yaml"
    weights_path = PROJECT_ROOT.parent / "yolo26n.pt"
    test_clip_dir = PROJECT_ROOT / "data" / "test_clip"
    img_dir = test_clip_dir / "img1"

    images = sorted(img_dir.glob("*.jpg"))
    if not images:
        print(f"Lỗi: Không tìm thấy ảnh trong {img_dir}")
        return 1

    print(f"[*] Input Data: {len(images)} frame ảnh từ {test_clip_dir.name}")
    print(f"[*] Model Detector: {weights_path.name} (YOLO Vehicle Detector)")
    print(f"[*] Association Tracker: ByteTrack (Kalman Filter + 2-Stage IoU Match)")

    # 1. Initialize Tracker
    tracker = VisualTracker(config_path=config_path, weights_path=weights_path)

    # 2. Run Tracking
    print("\n>>> BẮT ĐẦU THEO DÕI ĐỐI TƯỢNG (TRACKING INFERENCE)...")
    t0 = time.time()
    tracked_frames = tracker.track_frames(images, verbose=True)
    t_elapsed = time.time() - t0
    fps = len(images) / t_elapsed
    print(f"\n[✓] Hoàn thành tracking: {len(images)} frame trong {t_elapsed:.2f}s (~{fps:.1f} FPS)")

    # 3. Export MOT 1.1
    outputs_dir = PROJECT_ROOT / "outputs"
    mot_out = outputs_dir / "tracks_mot.txt"
    tracker.save_mot(tracked_frames, mot_out)

    # 4. Generate Visualizations
    print("\n>>> XUẤT VIDEO & ẢNH MINH HỌA...")
    visualizer = TrackingVisualizer(fps=12.5)
    video_out = outputs_dir / "tracking_result.mp4"
    visualizer.render_video(tracked_frames, video_out)

    # Render a 4-frame collage (frames 1, 20, 40, 60)
    grid_out = outputs_dir / "tracking_grid.jpg"
    selected_frames = [1, 20, 40, min(60, len(images))]
    visualizer.render_grid_summary(tracked_frames, grid_out, selected_frames)

    # 5. Metrics Analysis
    stats = analyze_tracks(tracked_frames)
    stats["inference_time_sec"] = round(t_elapsed, 2)
    stats["inference_fps"] = round(fps, 1)

    metrics_out = outputs_dir / "metrics_summary.json"
    metrics_out.write_text(json.dumps(stats, indent=2), encoding="utf-8")
    print(f"  Đã ghi thống kê: {metrics_out}")

    # 6. Display Summary Report
    print("\n" + "=" * 70)
    print("                    KẾT QUẢ TRACKING TEST")
    print("=" * 70)
    print(f"  • Tổng số frame xử lý  : {stats['total_frames_processed']}")
    print(f"  • Tổng số bounding box : {stats['total_detections']}")
    print(f"  • Số xe phân biệt (ID) : {stats['unique_track_count']} tracks")
    print(f"  • Tốc độ xử lý         : {stats['inference_fps']} FPS (trên CPU/Mac)")
    print("-" * 70)
    print(f"  {'Track ID':<10} {'Loại xe':<10} {'Xuất hiện':<16} {'Tổng frame':<14} {'Độ tin cậy'}")
    print("-" * 70)
    for tid, info in sorted(stats["tracks"].items()):
        frames_range = f"f:{info['first_frame']} -> f:{info['last_frame']}"
        print(f"  ID {tid:<7} {info['class']:<10} {frames_range:<16} {info['duration_frames']:<14} {info['avg_confidence'] * 100:.1f}%")
    print("=" * 70)
    print(f"[✓] File video đã tạo : {video_out}")
    print(f"[✓] File ảnh collage  : {grid_out}")
    print(f"[✓] File dữ liệu MOT  : {mot_out}")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
