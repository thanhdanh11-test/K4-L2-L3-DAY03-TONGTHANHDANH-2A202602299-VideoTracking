#!/usr/bin/env python3
"""Modular Tracking Engine using YOLO and ByteTrack/BoT-SORT."""

from __future__ import annotations

from pathlib import Path
import yaml
from ultralytics import YOLO


COCO_VEHICLES = {2: "car", 5: "bus", 7: "truck"}


class VisualTracker:
    def __init__(self, config_path: Path | str, weights_path: Path | str | None = None):
        self.config_path = Path(config_path)
        with open(self.config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        weights = weights_path or self.config.get("model_weights", "yolo26n.pt")
        self.model = YOLO(str(weights))
        self.classes = self.config.get("classes", [2, 5, 7])
        self.conf = self.config.get("conf_threshold", 0.25)
        self.iou = self.config.get("iou_threshold", 0.70)
        self.imgsz = self.config.get("img_size", 960)
        self.tracker_type = self.config.get("tracker_type", "bytetrack")

    def track_frames(self, image_paths: list[Path], verbose: bool = True) -> list[dict]:
        """Track objects through a sequence of frames.
        
        Returns a list of dicts:
            {
                'frame_idx': int (1-based),
                'image_path': Path,
                'detections': [
                    {'track_id': int, 'box': [x1, y1, w, h], 'conf': float, 'cls': str}
                ]
            }
        """
        results_per_frame = []
        tracker_yaml = f"{self.tracker_type}.yaml"

        total = len(image_paths)
        for idx, img_path in enumerate(image_paths, start=1):
            preds = self.model.track(
                source=str(img_path),
                persist=True,
                tracker=tracker_yaml,
                conf=self.conf,
                iou=self.iou,
                imgsz=self.imgsz,
                classes=self.classes,
                verbose=False,
            )

            boxes = preds[0].boxes
            frame_dets = []
            if boxes is not None and boxes.id is not None:
                xyxy_list = boxes.xyxy.tolist()
                id_list = boxes.id.int().tolist()
                conf_list = boxes.conf.tolist()
                cls_list = boxes.cls.int().tolist()

                for xyxy, track_id, score, cls_id in zip(xyxy_list, id_list, conf_list, cls_list):
                    x1, y1, x2, y2 = xyxy
                    w = x2 - x1
                    h = y2 - y1
                    cls_name = COCO_VEHICLES.get(cls_id, "vehicle")
                    frame_dets.append({
                        "track_id": int(track_id),
                        "box": [float(x1), float(y1), float(w), float(h)],
                        "conf": float(score),
                        "cls": cls_name,
                    })

            results_per_frame.append({
                "frame_idx": idx,
                "image_path": img_path,
                "detections": frame_dets,
            })

            if verbose and (idx % 20 == 0 or idx == total):
                active_ids = len(frame_dets)
                print(f"  Frame {idx}/{total} -> {active_ids} active vehicle tracks")

        return results_per_frame

    @staticmethod
    def save_mot(results_per_frame: list[dict], output_file: Path | str) -> None:
        """Export detections to standard MOT 1.1 CSV format."""
        out_path = Path(output_file)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        lines = []
        for frame in results_per_frame:
            f_idx = frame["frame_idx"]
            for det in frame["detections"]:
                tid = det["track_id"]
                x, y, w, h = det["box"]
                c = det["conf"]
                lines.append(f"{f_idx},{tid},{x:.2f},{y:.2f},{w:.2f},{h:.2f},{c:.4f},-1,-1,-1\n")

        out_path.write_text("".join(lines), encoding="utf-8")
        print(f"  Đã lưu MOT 1.1: {out_path} ({len(lines)} dòng)")
