from video2audio.caption import describe_ai_captions, describe_shapes, srt_from_captions
from video2audio.vision import Detection


def test_shape_caption_bilingual():
    obj0 = Detection("circle", "red", 40, 70, 1200, (20, 50, 40, 40))
    obj1 = Detection("circle", "red", 120, 70, 1200, (100, 50, 40, 40))
    en, motion = describe_shapes([[obj0], [obj1]], "en")
    fr, _ = describe_shapes([[obj0], [obj1]], "fr")
    assert motion == "right"
    assert "red circle" in en and "to the right" in en
    assert "cercle rouge" in fr and "vers la droite" in fr


def test_no_detected_shapes_is_not_hallucinated():
    text, direction = describe_shapes([[], []])
    assert "No colored geometric shapes" in text
    assert direction == "unknown"


def test_ai_caption_dedupes_frames():
    result = describe_ai_captions(["a cat on the sofa", "a cat on the sofa", "a dog outside"], 0)
    assert result.count("cat") == 1
    assert "dog" in result


def test_srt_time_format():
    content = srt_from_captions(["frame one", "frame two"], [0, 1.2], 2)
    assert "00:00:00,000 --> 00:00:01,200" in content
    assert "00:00:01,200 --> 00:00:02,000" in content
