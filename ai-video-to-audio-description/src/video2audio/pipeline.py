"""End-to-end: decode -> sample -> perceive -> describe -> narrate -> export."""
from __future__ import annotations
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import time

import cv2

from .caption import describe_shapes, describe_ai_captions, srt_from_captions
from .tts import synthesize
from .video import read_video, frame_difference
from .vision import detect_shapes, annotated_frame


@dataclass
class ProcessingResult:
    video: str
    backend: str
    narration: str
    output_dir: str
    predicted_shape: str | None
    predicted_color: str | None
    direction: str | None
    duration_seconds: float
    sample_count: int
    scene_change_score: float
    audio_generated: bool
    processing_seconds: float

    def to_dict(self) -> dict:
        return asdict(self)


def process_video(video: str | Path, output_dir: str | Path, *, backend: str = "shapes",
                  language: str = "en", samples: int = 5, audio: bool = True,
                  blip_captioner=None) -> ProcessingResult:
    """Process a real video (BLIP) or synthetic colored shapes (baseline).

    shapes: deterministic geometric shape detector, NOT general visual AI.
    blip: pretrained image-to-text model (download + torch required).
    """
    if backend not in {"shapes", "blip"}:
        raise ValueError("backend must be 'shapes' or 'blip'")
    if language not in {"en", "fr"}:
        raise ValueError("language must be 'en' or 'fr'")
    if backend == "blip" and language != "en":
        raise ValueError("BLIP captions are currently English-only; choose --language en")
    start = time.perf_counter()
    video = read_video(video, samples=samples)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    frame_score = frame_difference(video.frames)
    detected_shape, detected_color, direction = None, None, None
    observations = []
    if backend == "shapes":
        observations = [detect_shapes(frame) for frame in video.frames]
        narration, direction = describe_shapes(observations, language)
        top = next((ds[0] for ds in observations if ds), None)
        if top:
            detected_shape, detected_color = top.shape, top.color
        frame_captions = []
        for ds in observations:
            if ds:
                d = ds[0]
                frame_captions.append(f"{d.color} {d.shape}" if language == "en" else f"{d.shape} de couleur {d.color}")
            else:
                frame_captions.append("No shape detected" if language == "en" else "Aucune forme détectée")
    else:
        if blip_captioner is None:
            from .ai import BLIPCaptioner
            blip_captioner = BLIPCaptioner()
        frame_captions = [blip_captioner.caption(frame) for frame in video.frames]
        narration = describe_ai_captions(frame_captions, frame_score)

    # Artifacts are deliberately simple portable formats (TXT, JSON, SRT, JPG, WAV).
    (output_dir / "description.txt").write_text(narration + "\n", encoding="utf-8")
    (output_dir / "captions.srt").write_text(
        srt_from_captions(frame_captions, video.timestamps, video.duration_seconds), encoding="utf-8")
    thumbnail = annotated_frame(video.frames[len(video.frames) // 2],
                                observations[len(observations)//2]) if backend == "shapes" else video.frames[len(video.frames)//2]
    if not cv2.imwrite(str(output_dir / "preview.jpg"), thumbnail):
        raise OSError("Failed to write preview.jpg")
    audio_generated = False
    if audio:
        synthesize(narration, output_dir / "description.wav", language=language)
        audio_generated = True
    result = ProcessingResult(
        video=str(video.path), backend=backend, narration=narration,
        output_dir=str(output_dir), predicted_shape=detected_shape,
        predicted_color=detected_color, direction=direction,
        duration_seconds=video.duration_seconds, sample_count=len(video.frames),
        scene_change_score=round(frame_score, 3), audio_generated=audio_generated,
        processing_seconds=round(time.perf_counter() - start, 3))
    details = result.to_dict()
    details.update({
        "model_provenance": ("classical OpenCV HSV/contours + rule-based captions"
                             if backend == "shapes" else "Salesforce/blip-image-captioning-base (pretrained; model-derived)"),
        "warnings": (["Synthetic-shape-only baseline: not suitable for natural videos"]
                     if backend == "shapes" else ["Frame-level captions may be inaccurate; motion from frame differences is not object tracking"]),
        "frame_observations": [
            {"timestamp": stamp, "caption": caption,
             "detections": ([d.to_dict() for d in observations[i]] if backend == "shapes" else [])}
            for i, (stamp, caption) in enumerate(zip(video.timestamps, frame_captions))
        ],
    })
    (output_dir / "result.json").write_text(json.dumps(details, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result
