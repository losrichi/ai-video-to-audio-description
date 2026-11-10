"""Time-based sampling of video frames with OpenCV."""
from dataclasses import dataclass
from pathlib import Path
import cv2
import numpy as np

SUPPORTED = {".mp4", ".mov", ".avi", ".mkv", ".webm"}


@dataclass
class VideoFrames:
    path: str
    frames: list[np.ndarray]
    timestamps: list[float]
    duration_seconds: float
    fps: float
    frame_count: int
    width: int
    height: int


def read_video(path: str | Path, samples: int = 5) -> VideoFrames:
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Video not found: {path}")
    if path.suffix.lower() not in SUPPORTED:
        raise ValueError(f"Unsupported video format {path.suffix!r}; expected one of {sorted(SUPPORTED)}")
    if not 1 <= samples <= 32:
        raise ValueError("samples must be between 1 and 32")
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {path}")
    try:
        fps = float(cap.get(cv2.CAP_PROP_FPS))
        count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        if fps <= 0 or count <= 0 or width <= 0 or height <= 0:
            raise ValueError("Invalid video metadata: frame count, FPS or dimensions")
        indices = sorted(set(int(round(x)) for x in np.linspace(0, count - 1, min(samples, count))))
        frames, timestamps = [], []
        for index in indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, index)
            ok, frame = cap.read()
            if not ok or frame is None:
                raise ValueError(f"Unable to decode frame {index} in {path}")
            frames.append(frame)
            timestamps.append(round(index / fps, 3))
    finally:
        cap.release()
    return VideoFrames(str(path), frames, timestamps, round(count / fps, 3), fps, count, width, height)


def frame_difference(frames: list[np.ndarray]) -> float:
    """Motion indicator; NOT a semantic action detector and can reflect camera motion."""
    if len(frames) <= 1:
        return 0.0
    grays = [cv2.resize(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY), (128, 72)) for f in frames]
    changes = [np.mean(cv2.absdiff(a, b)) for a, b in zip(grays, grays[1:])]
    return float(np.mean(changes))
