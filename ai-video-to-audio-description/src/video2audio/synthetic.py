"""Procedurally generate reproducible, license-free benchmark videos.

Labels are written to a separate manifest; inference never reads the manifest.
"""
from __future__ import annotations
import csv
from dataclasses import dataclass, asdict
from pathlib import Path

import cv2
import numpy as np

SHAPES = ("circle", "square", "triangle", "rectangle")
COLORS_BGR = {
    "red": (50, 60, 225), "green": (65, 175, 50),
    "blue": (220, 100, 45), "yellow": (35, 205, 235),
}
DIRECTIONS = ("left", "right", "up", "down", "still")


@dataclass
class SyntheticLabel:
    video_id: str
    filename: str
    seed: int
    shape: str
    color: str
    direction: str
    fps: int
    frames: int
    synthetic: bool = True

    def to_dict(self):
        return asdict(self)


def make_label(index: int, seed: int = 2026) -> SyntheticLabel:
    rng = np.random.default_rng(seed + index * 37)
    shape = SHAPES[index % len(SHAPES)]
    color = list(COLORS_BGR)[(index // len(SHAPES)) % len(COLORS_BGR)]
    direction = DIRECTIONS[(index // (len(SHAPES)*len(COLORS_BGR))) % len(DIRECTIONS)]
    # 120 covers all 4 shapes / 4 colors / 5 directions, with repeats and varied seeds.
    return SyntheticLabel(f"synthetic_{index:03d}", f"synthetic_{index:03d}.mp4",
                          int(rng.integers(0, 2_000_000)), shape, color, direction, 10, 20)


def _render_object(canvas: np.ndarray, shape: str, color_bgr: tuple, x: int, y: int, size: int):
    if shape == "circle":
        cv2.circle(canvas, (x, y), size, color_bgr, -1, cv2.LINE_AA)
    elif shape == "square":
        cv2.rectangle(canvas, (x-size, y-size), (x+size, y+size), color_bgr, -1, cv2.LINE_AA)
    elif shape == "rectangle":
        cv2.rectangle(canvas, (x-int(size*1.45), y-int(size*.68)),
                      (x+int(size*1.45), y+int(size*.68)), color_bgr, -1, cv2.LINE_AA)
    elif shape == "triangle":
        pts = np.array([(x, y-size-5), (x-size-5, y+size), (x+size+5, y+size)], dtype=np.int32)
        cv2.fillConvexPoly(canvas, pts, color_bgr, cv2.LINE_AA)


def write_synthetic_video(path: str | Path, label: SyntheticLabel, *, width: int = 320,
                          height: int = 200) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(label.seed)
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), label.fps, (width, height))
    if not writer.isOpened():
        raise RuntimeError("Cannot create MP4 file (OpenCV mp4v codec unavailable)")
    size = int(rng.integers(20, 27))
    x0 = int(rng.integers(100, 220))
    y0 = int(rng.integers(70, 135))
    amplitude = int(rng.integers(42, 70))
    velocity = {"right": (amplitude, 0), "left": (-amplitude, 0),
                "up": (0, -amplitude), "down": (0, amplitude), "still": (0, 0)}[label.direction]
    try:
        for i in range(label.frames):
            frame = np.full((height, width, 3), (237, 239, 241), dtype=np.uint8)
            # Neutral grid and header (low saturation; never interpreted as objects).
            for gx in range(0, width, 40):
                cv2.line(frame, (gx, 0), (gx, height), (224, 227, 229), 1)
            for gy in range(0, height, 40):
                cv2.line(frame, (0, gy), (width, gy), (224, 227, 229), 1)
            cv2.putText(frame, "SYNTHETIC VIDEO", (10, 17), cv2.FONT_HERSHEY_SIMPLEX,
                        0.42, (115, 118, 121), 1, cv2.LINE_AA)
            phase = i / (label.frames - 1) if label.frames > 1 else 0
            x = round(x0 + velocity[0] * phase)
            y = round(y0 + velocity[1] * phase)
            _render_object(frame, label.shape, COLORS_BGR[label.color], x, y, size)
            writer.write(frame)
    finally:
        writer.release()
    if not path.exists() or path.stat().st_size < 200:
        raise RuntimeError(f"Video creation failed for {path}")
    return path


def generate_collection(out_dir: str | Path, count: int = 120,
                        seed: int = 2026) -> list[SyntheticLabel]:
    if count < 1:
        raise ValueError("count must be >= 1")
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    labels = []
    for i in range(count):
        label = make_label(i, seed)
        write_synthetic_video(out_dir / label.filename, label)
        labels.append(label)
    with (out_dir / "ground_truth.csv").open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(labels[0].to_dict()))
        writer.writeheader()
        writer.writerows([label.to_dict() for label in labels])
    return labels
