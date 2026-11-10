"""Regenerate four synthetic samples and their verified narrated output."""
import json
from pathlib import Path
import shutil
import subprocess
from video2audio.synthetic import make_label, write_synthetic_video
from video2audio.pipeline import process_video

ROOT = Path(__file__).resolve().parents[1]
VIDEOS = ROOT / "examples" / "videos"
RESULTS = ROOT / "examples" / "results"

if __name__ == "__main__":
    entries = []
    ids = [0, 5, 42, 75]
    for index in ids:
        label = make_label(index)
        video_path = write_synthetic_video(VIDEOS / label.filename, label)
        if shutil.which("ffmpeg"):
            # OpenCV's default mp4v codec is not reliably playable in browsers.
            # Convert published examples to H.264 so the GitHub Pages demo works.
            candidate = video_path.with_suffix(".h264.mp4")
            subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(video_path),
                            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                            str(candidate)], check=True)
            candidate.replace(video_path)
        else:
            print("WARNING: ffmpeg missing; example MP4 may not play in browsers")
        result = process_video(video_path, RESULTS / label.video_id, audio=True)
        entries.append({"label": label.to_dict(), "result": result.to_dict()})
        print(f"{video_path.name}: {result.narration}")
    (ROOT / "examples" / "manifest.json").write_text(
        json.dumps(entries, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
