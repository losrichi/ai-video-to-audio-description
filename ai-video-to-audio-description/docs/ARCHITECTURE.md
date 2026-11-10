# Architecture

The architecture chart in `architecture.svg` is a schematic of implemented components, not a claim that every model has been evaluated.

`Video MP4 → OpenCV decoder → 5 spaced frames → one of two vision backends → textual narration → eSpeak / pyttsx3 → WAV + SRT + JSON + JPG`.

**Shape backend:** HSV contour segmentation → polygon shape classification → largest object centroid comparison between first/last sample → deterministic English/French templates. Best suited to the synthetic videos in this repository.

**BLIP backend:** open-source pretrained vision-language model → per-frame English captions → simple deduplication and chronological text aggregation. Uses image differences as a scene-change indication, **not** a reliable direction or object-motion estimate.

CLI and Gradio both call the same `process_video` API. Benchmarking calls the same API without the ground-truth labels, and writes predictions for inspection.
