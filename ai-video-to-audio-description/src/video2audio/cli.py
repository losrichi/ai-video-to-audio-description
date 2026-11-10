"""video2audio command line entrypoint."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

from .benchmark import run_benchmark
from .pipeline import process_video


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="video2audio", description="Decode video, generate an honest visual description and synthesize WAV audio")
    sub = parser.add_subparsers(dest="command", required=True)
    describe = sub.add_parser("describe", help="Process one video")
    describe.add_argument("--input", required=True, type=Path, help="Input MP4/MOV/AVI/MKV/WEBM")
    describe.add_argument("--output", default=Path("outputs/result"), type=Path)
    describe.add_argument("--backend", choices=["shapes", "blip"], default="shapes")
    describe.add_argument("--language", choices=["en", "fr"], default="en")
    describe.add_argument("--samples", type=int, default=5)
    describe.add_argument("--no-audio", action="store_true", help="Export transcript without WAV")
    batch = sub.add_parser("batch", help="Process video files in a directory")
    batch.add_argument("--input-dir", required=True, type=Path)
    batch.add_argument("--output-dir", default=Path("outputs/batch"), type=Path)
    batch.add_argument("--backend", choices=["shapes", "blip"], default="shapes")
    batch.add_argument("--language", choices=["en", "fr"], default="en")
    batch.add_argument("--no-audio", action="store_true")
    bench = sub.add_parser("benchmark", help="Generate and process N synthetic videos")
    bench.add_argument("--count", type=int, default=120)
    bench.add_argument("--output-dir", default=Path("benchmarks"), type=Path)
    bench.add_argument("--seed", type=int, default=2026)
    bench.add_argument("--no-audio", action="store_true")
    bench.add_argument("--keep-videos", action="store_true")
    return parser


def main(argv=None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "describe":
        print(json.dumps(process_video(args.input, args.output, backend=args.backend,
                                       language=args.language, samples=args.samples,
                                       audio=not args.no_audio).to_dict(), indent=2, ensure_ascii=False))
    elif args.command == "batch":
        from .video import SUPPORTED
        if not args.input_dir.is_dir():
            raise SystemExit(f"Missing input directory: {args.input_dir}")
        inputs = sorted(p for p in args.input_dir.rglob("*") if p.suffix.lower() in SUPPORTED)
        if not inputs:
            raise SystemExit("No supported video files found")
        succeeded, failures = 0, []
        captioner = None
        if args.backend == "blip":
            from .ai import BLIPCaptioner
            captioner = BLIPCaptioner()  # load once for all clips
        for i, path in enumerate(inputs):
            print(f"[{i+1}/{len(inputs)}] {path.name}")
            try:
                relative = path.relative_to(args.input_dir)
                target = args.output_dir / relative.with_suffix("")
                process_video(path, target, backend=args.backend,
                              language=args.language, audio=not args.no_audio,
                              blip_captioner=captioner)
                succeeded += 1
            except Exception as exc:
                failures.append({"video": str(path), "error": str(exc)})
        args.output_dir.mkdir(parents=True, exist_ok=True)
        report = {"total": len(inputs), "successful": succeeded, "failures": failures}
        (args.output_dir / "batch_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2))
        return 1 if failures else 0
    else:
        metrics = run_benchmark(args.output_dir, count=args.count, seed=args.seed,
                                audio=not args.no_audio, persist_videos=args.keep_videos)
        print(json.dumps(metrics, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
