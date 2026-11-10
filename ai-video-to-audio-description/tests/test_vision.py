import pytest
from video2audio.synthetic import make_label, write_synthetic_video
from video2audio.vision import detect_shapes, movement
from video2audio.video import read_video


@pytest.mark.parametrize("index", [0, 1, 2, 3, 5, 42, 75])
def test_synthetic_shape_and_color_detection(index, tmp_path):
    label = make_label(index)
    path = write_synthetic_video(tmp_path / f"{index}.mp4", label)
    frames = read_video(path, samples=5)
    observations = [detect_shapes(frame) for frame in frames.frames]
    assert observations[0]
    assert observations[0][0].shape == label.shape
    assert observations[0][0].color == label.color
    assert movement(observations) == label.direction
