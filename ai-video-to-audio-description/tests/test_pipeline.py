import json
import shutil
from pathlib import Path

import pytest
from video2audio.pipeline import process_video
from video2audio.synthetic import make_label, write_synthetic_video


def test_pipeline_writes_valid_files(tmp_path):
    label = make_label(0)
    source = write_synthetic_video(tmp_path / "clip.mp4", label)
    result = process_video(source, tmp_path / "result", audio=False)
    assert result.predicted_shape == label.shape
    assert result.predicted_color == label.color
    assert (tmp_path / "result" / "preview.jpg").stat().st_size > 100
    assert (tmp_path / "result" / "captions.srt").stat().st_size > 20
    assert (tmp_path / "result" / "description.txt").stat().st_size > 10
    obj = json.loads((tmp_path / "result" / "result.json").read_text())
    assert obj["backend"] == "shapes"
    assert "classical OpenCV" in obj["model_provenance"]
    assert obj["audio_generated"] is False


@pytest.mark.skipif(not (shutil.which("espeak") or shutil.which("espeak-ng")),
                    reason="eSpeak unavailable")
def test_full_pipeline_wav(tmp_path):
    source = write_synthetic_video(tmp_path / "clip.mp4", make_label(42))
    result = process_video(source, tmp_path / "output", audio=True)
    assert result.audio_generated is True
    raw = (tmp_path / "output" / "description.wav").read_bytes()
    assert raw[:4] == b"RIFF"
    assert raw[8:12] == b"WAVE"


def test_blip_backend_with_mock_model_no_download(tmp_path):
    class FakeCaptioner:
        def caption(self, frame):
            return "a colorful shape in a studio"

    source = write_synthetic_video(tmp_path / "clip.mp4", make_label(7))
    result = process_video(source, tmp_path / "output", backend="blip",
                           blip_captioner=FakeCaptioner(), audio=False)
    assert "colorful shape" in result.narration
    assert result.predicted_shape is None
    assert result.backend == "blip"


def test_blip_french_rejected(tmp_path):
    source = write_synthetic_video(tmp_path / "clip.mp4", make_label(0))
    with pytest.raises(ValueError, match="English-only"):
        process_video(source, tmp_path / "output", backend="blip", language="fr", audio=False)
