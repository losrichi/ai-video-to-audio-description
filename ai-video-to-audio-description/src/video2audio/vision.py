"""Honest, interpretable colored-geometric-shape detection for synthetic videos.

This is a classical computer-vision baseline, NOT a general object recognizer.
For real-world descriptions, use the optional BLIP backend.
"""
from dataclasses import dataclass, asdict
import cv2
import numpy as np


@dataclass
class Detection:
    shape: str
    color: str
    center_x: int
    center_y: int
    area: int
    bbox: tuple[int, int, int, int]

    def to_dict(self):
        return asdict(self)


def _name_color(hue: float) -> str:
    if hue < 12 or hue >= 168:
        return "red"
    if hue < 37:
        return "yellow"
    if hue < 88:
        return "green"
    if hue < 140:
        return "blue"
    return "red"  # generator emits only red, green, yellow, blue


def detect_shapes(frame: np.ndarray, min_area: int = 180) -> list[Detection]:
    if frame is None or frame.size == 0:
        return []
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # The procedurally generated demos use high-saturation solid foregrounds.
    mask = cv2.inRange(hsv, (0, 105, 75), (179, 255, 255))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    detections = []
    for contour in contours:
        area = float(cv2.contourArea(contour))
        if area < min_area:
            continue
        perim = cv2.arcLength(contour, True)
        if perim <= 0:
            continue
        poly = cv2.approxPolyDP(contour, 0.035 * perim, True)
        x, y, w, h = cv2.boundingRect(contour)
        circularity = 4 * np.pi * area / (perim * perim)
        if len(poly) == 3:
            shape = "triangle"
        elif len(poly) == 4:
            shape = "square" if 0.85 <= w / max(h, 1) <= 1.18 else "rectangle"
        elif circularity > 0.72:
            shape = "circle"
        else:
            shape = "unknown shape"
        # Foreground median hue inside THIS contour (avoids background contamination).
        local_mask = np.zeros(mask.shape, dtype=np.uint8)
        cv2.drawContours(local_mask, [contour], -1, 255, -1)
        hues = hsv[:, :, 0][local_mask > 0]
        color = _name_color(float(np.median(hues))) if hues.size else "unknown"
        moments = cv2.moments(contour)
        cx = int(moments["m10"] / moments["m00"]) if moments["m00"] else x + w // 2
        cy = int(moments["m01"] / moments["m00"]) if moments["m00"] else y + h // 2
        detections.append(Detection(shape, color, cx, cy, round(area), (x, y, w, h)))
    return sorted(detections, key=lambda d: d.area, reverse=True)


def movement(detections_by_frame: list[list[Detection]], tolerance: int = 10) -> str:
    """Track largest matching shape/color in first and last observation."""
    valid = [ds for ds in detections_by_frame if ds]
    if len(valid) < 2:
        return "unknown"
    first = valid[0][0]
    matching = [d for d in valid[-1] if (d.shape, d.color) == (first.shape, first.color)]
    if not matching:
        return "unknown"
    last = matching[0]
    dx, dy = last.center_x - first.center_x, last.center_y - first.center_y
    if abs(dx) < tolerance and abs(dy) < tolerance:
        return "still"
    if abs(dx) >= abs(dy):
        return "right" if dx > 0 else "left"
    return "down" if dy > 0 else "up"


def annotated_frame(frame: np.ndarray, detections: list[Detection]) -> np.ndarray:
    result = frame.copy()
    for d in detections:
        x, y, w, h = d.bbox
        cv2.rectangle(result, (x, y), (x + w, y + h), (25, 25, 25), 2)
        cv2.putText(result, f"{d.color} {d.shape}", (x, max(y - 8, 15)), cv2.FONT_HERSHEY_SIMPLEX,
                    0.48, (15, 15, 15), 2, cv2.LINE_AA)
    return result
