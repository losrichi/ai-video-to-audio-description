"""Reproducible processing benchmark on 120 generated videos.

Measures geometric shape/color/direction recognition only. NOT a benchmark of
real-world caption correctness or accessibility quality.
"""
from __future__ import annotations
import csv
import json
from pathlib import Path
import tempfile
import time

from .pipeline import process_video
from .synthetic import generate_collection


def run_benchmark(output_dir: str | Path, count: int = 120, *, audio: bool = True,
                  seed: int = 2026, persist_videos: bool = False) -> dict:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="video2audio-bench-") as tmp:
        videos_dir = output_dir / "generated_videos" if persist_videos else Path(tmp) / "videos"
        labels = generate_collection(videos_dir, count=count, seed=seed)
        rows = []
        for label in labels:
            # Result files and WAVs are written to temp to keep published repo small.
            result_dir = Path(tmp) / "outputs" / label.video_id
            result = process_video(videos_dir / label.filename, result_dir,
                                   backend="shapes", samples=5, audio=audio)
            if audio and not (result_dir / "description.wav").exists():
                raise AssertionError(f"Missing synthesized WAV for {label.video_id}")
            rows.append({
                "video_id": label.video_id, "synthetic": True,
                "truth_shape": label.shape, "pred_shape": result.predicted_shape,
                "truth_color": label.color, "pred_color": result.predicted_color,
                "truth_direction": label.direction, "pred_direction": result.direction,
                "shape_correct": int(label.shape == result.predicted_shape),
                "color_correct": int(label.color == result.predicted_color),
                "direction_correct": int(label.direction == result.direction),
                "audio_generated": int(result.audio_generated),
                "processing_seconds": result.processing_seconds,
                "narration": result.narration,
            })
        # Labels are published; audio and generated video binary files are reproducible on demand.
        manifest = output_dir / "ground_truth.csv"
        manifest.write_bytes((videos_dir / "ground_truth.csv").read_bytes())
    total = len(rows)
    stats = {
        "dataset_type": "procedurally generated synthetic colored geometric shapes",
        "benchmark_scope": "shape, color and dominant motion detection; NOT natural-video evaluation",
        "seed": seed,
        "sampled_frames_per_video": 5,
        "video_count": total,
        "audio_requested": audio,
        "audio_files_verified": sum(r["audio_generated"] for r in rows),
        "shape_accuracy": round(sum(r["shape_correct"] for r in rows) / total, 4),
        "color_accuracy": round(sum(r["color_correct"] for r in rows) / total, 4),
        "direction_accuracy": round(sum(r["direction_correct"] for r in rows) / total, 4),
        "average_processing_seconds": round(sum(r["processing_seconds"] for r in rows) / total, 3),
        "elapsed_wall_seconds": round(time.perf_counter() - started, 3),
        "notes": [
            "The test videos are programmatically generated and are not real-world footage.",
            "Evaluation labels are never passed into inference.",
            "Video/audio binaries are regenerated using the benchmark command and excluded from the ZIP.",
            "Caption naturalness and speech intelligibility require human review; not measured here.",
        ],
    }
    with (output_dir / "predictions.csv").open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (output_dir / "metrics.json").write_text(json.dumps(stats, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return stats
