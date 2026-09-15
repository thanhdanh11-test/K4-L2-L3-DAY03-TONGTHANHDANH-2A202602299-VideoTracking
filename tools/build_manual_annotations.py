#!/usr/bin/env python3
"""Build the two independently observed MOT 1.1 annotation files.

The keyframes below were read manually from the supplied images.  Intermediate
boxes use the same linear interpolation that CVAT applies between rectangle
track keyframes.  No reference labels or automatic tracker are used.
"""

from __future__ import annotations

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]


def interpolate(anchors: dict[int, tuple[float, float, float, float]]):
    frames = sorted(anchors)
    for left, right in zip(frames, frames[1:]):
        start, end = anchors[left], anchors[right]
        span = right - left
        for frame in range(left, right):
            ratio = (frame - left) / span
            yield frame, tuple(a + (b - a) * ratio for a, b in zip(start, end))
    yield frames[-1], anchors[frames[-1]]


def write_clip(name: str, tracks: dict[int, dict[int, tuple[float, float, float, float]]]):
    rows: list[tuple[int, int, float, float, float, float]] = []
    for track_id, anchors in tracks.items():
        for frame, (x, y, w, h) in interpolate(anchors):
            x = min(959.0, max(0.0, x))
            y = min(539.0, max(0.0, y))
            w = min(w, 960.0 - x)
            h = min(h, 540.0 - y)
            rows.append((frame, track_id, x, y, w, h))
    rows.sort()

    target = ROOT / "annotations" / name / "gt.txt"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "".join(
            f"{frame},{track_id},{x:.2f},{y:.2f},{w:.2f},{h:.2f},1,1,1\n"
            for frame, track_id, x, y, w, h in rows
        ),
        encoding="utf-8",
    )

    archive = ROOT / "annotations" / f"{name}-mot.zip"
    with ZipFile(archive, "w", ZIP_DEFLATED) as bundle:
        bundle.write(target, "gt/gt.txt")
        # "vehicle" is not one of MOTChallenge's built-in pedestrian classes,
        # therefore CVAT requires an explicit class-id-to-label mapping.
        bundle.writestr("gt/labels.txt", "vehicle\n")
    print(f"{name}: {len(rows)} boxes -> {target}")


CORE = {
    # White SUV parked beside the upper road.
    1: {1: (207, 251, 96, 40), 100: (207, 251, 96, 40), 184: (207, 251, 96, 40)},
    # Silver sedan already crossing the foreground at the start.
    2: {1: (121, 340, 150, 57), 5: (68, 354, 132, 57), 8: (0, 367, 98, 58), 11: (0, 378, 25, 42)},
    # Orange/green taxi crossing right-to-left.
    3: {1: (731, 268, 83, 40), 10: (606, 286, 88, 44), 20: (443, 307, 113, 51), 30: (263, 335, 128, 61), 40: (38, 382, 141, 75), 45: (0, 404, 28, 60)},
    # Articulated city bus.
    4: {52: (953, 224, 7, 54), 60: (915, 229, 45, 70), 80: (775, 236, 185, 92), 100: (569, 256, 247, 126), 120: (237, 305, 375, 162), 140: (0, 356, 291, 184), 148: (0, 392, 102, 148), 151: (0, 410, 35, 130)},
    # Dark sedan on the lane behind the bus.
    5: {80: (762, 258, 60, 39), 88: (676, 264, 72, 40), 96: (579, 270, 76, 41), 104: (472, 277, 82, 42), 112: (361, 283, 101, 43), 120: (234, 291, 119, 45), 128: (95, 299, 134, 47), 136: (0, 307, 81, 48), 140: (0, 311, 10, 43)},
    # Silver minivan following on the upper roadway.
    6: {96: (801, 250, 45, 36), 104: (691, 255, 85, 39), 112: (595, 261, 111, 42), 120: (482, 267, 106, 45), 128: (364, 275, 112, 47), 136: (244, 282, 118, 49), 144: (102, 289, 135, 51), 152: (0, 299, 94, 53), 156: (0, 305, 27, 48)},
    # White box truck entering from the right and remaining at clip end.
    7: {106: (949, 216, 11, 52), 112: (920, 217, 40, 62), 120: (880, 219, 80, 66), 128: (833, 222, 101, 68), 136: (780, 225, 98, 71), 144: (722, 228, 101, 72), 152: (650, 232, 111, 73), 160: (571, 237, 122, 71), 168: (484, 242, 132, 72), 176: (397, 248, 130, 71), 184: (303, 255, 137, 69), 190: (229, 260, 151, 64)},
    # Red sedan in the closest lane, moving left-to-right.
    8: {135: (697, 520, 104, 20), 140: (737, 494, 122, 46), 144: (769, 471, 126, 69), 148: (806, 451, 121, 76), 152: (839, 435, 111, 78), 156: (869, 418, 91, 76), 160: (895, 404, 65, 67), 164: (920, 392, 40, 60), 168: (943, 382, 17, 49)},
}


WARMUP = {
    # Two stopped buses remain visible along the top edge for the whole clip.
    1: {1: (307, 0, 402, 111), 60: (307, 0, 402, 111)},
    2: {1: (96, 0, 216, 63), 60: (96, 0, 216, 63)},
    # White sedan leaving the upper lane.
    3: {1: (54, 65, 121, 52), 4: (13, 55, 116, 51), 7: (0, 50, 58, 43)},
    # Dark sedan on the upper moving lane.
    4: {10: (929, 190, 31, 57), 15: (700, 146, 230, 92), 20: (518, 119, 232, 86), 25: (379, 91, 188, 78), 30: (273, 73, 158, 69), 35: (183, 61, 135, 62), 40: (115, 53, 120, 59), 45: (58, 43, 107, 55), 50: (6, 36, 95, 49), 55: (0, 31, 48, 43), 60: (0, 27, 9, 35)},
    # Black sedan crossing the close lane.
    5: {14: (0, 164, 36, 62), 20: (0, 184, 142, 112), 25: (58, 226, 232, 159), 30: (214, 292, 340, 190), 35: (473, 391, 365, 149), 38: (735, 458, 225, 82)},
    # Orange/blue taxi entering from the right.
    6: {28: (940, 199, 20, 43), 30: (868, 183, 92, 70), 35: (651, 129, 203, 89), 40: (485, 102, 200, 82), 45: (351, 79, 176, 74), 50: (249, 66, 158, 65), 55: (167, 56, 128, 58), 60: (101, 48, 115, 54)},
}


if __name__ == "__main__":
    write_clip("clip_01", CORE)
    write_clip("clip_02", WARMUP)
