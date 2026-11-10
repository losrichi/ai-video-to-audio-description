import pytest
from video2audio.synthetic import make_label, write_synthetic_video
from video2audio.video import read_video, frame_difference


def test_video_sampling_and_metadata(tmp_path):
    path = write_synthetic_video(tmp_path / "test.mp4", make_label(0))
    sampled = read_video(path, samples=5)
    assert sampled.frame_count == 20
    assert sampled.fps == 10
    assert sampled.duration_seconds == 2
    assert len(sampled.frames) == 5
    assert sampled.timestamps[0] == 0
    assert sampled.timestamps[-1] == 1.9
    assert frame_difference(sampled.frames) >= 0


def test_missing_video_is_explained(tmp_path):
    with pytest.raises(FileNotFoundError):
        read_video(tmp_path / "missing.mp4")


def test_invalid_sample_count(tmp_path):
    path = write_synthetic_video(tmp_path / "test.mp4", make_label(3))
    with pytest.raises(ValueError, match="samples"):
        read_video(path, samples=100)
