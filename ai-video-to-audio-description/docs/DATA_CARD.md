# Data card — Synthetic video benchmark

## Purpose
Evaluate whether a classical computer-vision baseline can detect synthetic geometric shapes and movement direction, then generate an audible narration end to end.

## Origin and consent
All assets are generated locally by `src/video2audio/synthetic.py` using NumPy and OpenCV. No videos of real people, copyrighted footage or personal data are included. License-free for this project (MIT).

## Construction
Each MP4 has 320×200 pixels, 10 FPS, 20 frames (~2 seconds), a neutral grayscale grid and exactly one colored object. Shapes: `circle`, `square`, `rectangle`, `triangle`. Colors: `red`, `green`, `blue`, `yellow`. Movement: `left`, `right`, `up`, `down`, `still`. The generator uses deterministic seeds derived from the experiment's base seed and sample index. Videos have small rendering variations and MP4 compression artifacts.

## Artifacts
- `examples/videos/`: four generated example MP4s.
- `benchmarks/ground_truth.csv`: all 120 expected labels.
- `benchmarks/predictions.csv`: 120 inference results including correctedness columns and synthesized-audio status.
- `benchmarks/metrics.json`: exact metrics (including machine-dependent runtime).

## Method
`video2audio benchmark --count 120 --seed 2026` generates 120 videos to a temporary directory. It passes video **files** (not labels) through the regular pipeline using 5 uniformly spaced frames per file. It synthesizes a WAV and checks that it exists. Only **after** each inference does the benchmark compare predictions with ground truth. Video and audio binaries are removed after execution unless videos are explicitly retained with `--keep-videos`.

## Known limitations
- **Synthetic/domain gap:** strong performance on these simple shapes is not evidence of general object/action recognition or the performance of BLIP.
- **Distribution:** one object per video, a small set of shapes/colors/directions, no real-world clutter or camera motion.
- **Audio metric:** confirms WAV file existence, **not** human-perceived intelligibility or accessibility quality.
- **Time:** runtime depends on CPU, codec and voice engine.
- **Reproducibility:** exact codecs may change slightly across platforms, affecting edge-case contour detection.

## Results
The published run processed 120/120 clips, verified 120/120 WAV files, and reached shape accuracy 100.00%, color accuracy 100.00%, direction accuracy 98.33%. This only establishes baseline functionality in a controlled domain.
