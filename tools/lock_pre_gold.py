#!/usr/bin/env python3
"""Khóa bản nhãn độc lập trước khi Lab Coach phát teaching reference."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from motlib import MotFormatError, by_track, parse_mot


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def current_git_head(root: Path) -> str | None:
    result = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def portable_path(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.name


def lock_annotation(annotation: Path, evidence_dir: Path, repo_root: Path) -> dict:
    if not annotation.is_file():
        raise ValueError(f"không tìm thấy annotation: {annotation}")

    try:
        detections = parse_mot(annotation)
    except MotFormatError as exc:
        raise ValueError(f"annotation MOT không hợp lệ: {exc}") from exc
    if not detections:
        raise ValueError("annotation rỗng; chưa thể khóa trước khi mở reference")

    source_digest = sha256(annotation)
    snapshot = evidence_dir / "gt.txt"
    manifest_path = evidence_dir / "manifest.json"

    if snapshot.exists():
        locked_digest = sha256(snapshot)
        if locked_digest != source_digest:
            raise ValueError(
                "đã có pre-gold snapshot với hash khác; không được ghi đè. "
                "Giữ snapshot cũ và trao đổi với Lab Coach."
            )
        if not manifest_path.is_file():
            raise ValueError("snapshot đã có nhưng thiếu manifest.json")
        return json.loads(manifest_path.read_text(encoding="utf-8"))

    evidence_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(annotation, snapshot)
    manifest = {
        "schema_version": 1,
        "locked_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": portable_path(annotation, repo_root),
        "snapshot": portable_path(snapshot, repo_root),
        "sha256": source_digest,
        "bytes": snapshot.stat().st_size,
        "rows": len(detections),
        "frames": len({det.frame for det in detections}),
        "track_ids": sorted(by_track(detections)),
        "git_head_before_lock": current_git_head(repo_root),
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--annotation",
        type=Path,
        default=Path("annotations/clip_01/gt.txt"),
    )
    parser.add_argument(
        "--evidence-dir",
        type=Path,
        default=Path("evidence/pre-gold/clip_01"),
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    try:
        manifest = lock_annotation(
            args.annotation.resolve(),
            args.evidence_dir.resolve(),
            args.repo_root.resolve(),
        )
    except ValueError as exc:
        print(f"LỖI: {exc}")
        return 2

    print("ĐÃ KHÓA PRE-GOLD")
    print(f"  snapshot: {manifest['snapshot']}")
    print(f"  sha256:   {manifest['sha256']}")
    print(f"  rows:     {manifest['rows']}")
    print(f"  tracks:   {len(manifest['track_ids'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
