"""Grounded text generation from detections or independent BLIP captions."""
from __future__ import annotations
import re
from .vision import Detection, movement

FR_COLORS = {"red": "rouge", "green": "vert", "yellow": "jaune", "blue": "bleu"}
FR_SHAPES = {"circle": "cercle", "square": "carré", "rectangle": "rectangle", "triangle": "triangle"}
FR_DIRECTIONS = {
    "left": "vers la gauche", "right": "vers la droite", "up": "vers le haut",
    "down": "vers le bas", "still": "reste presque immobile",
}
EN_DIRECTIONS = {"left": "to the left", "right": "to the right", "up": "upward", "down": "downward"}


def describe_shapes(detections: list[list[Detection]], language: str = "en") -> tuple[str, str]:
    """Return grounded full narration and inferred motion direction."""
    if language not in ("en", "fr"):
        raise ValueError("Supported languages: en, fr")
    valid = [ds for ds in detections if ds]
    if not valid:
        return ("No colored geometric shapes were detected in this clip."
                if language == "en" else "Aucune forme géométrique colorée détectée dans cette vidéo."), "unknown"
    obj = valid[0][0]
    direction = movement(detections)
    if language == "en":
        noun = f"{obj.color} {obj.shape}"
        desc = f"A {noun} is visible on a neutral background."
        if direction in EN_DIRECTIONS:
            desc += f" It moves {EN_DIRECTIONS[direction]}."
        elif direction == "still":
            desc += " It remains mostly stationary."
        else:
            desc += " Its movement could not be determined reliably."
        return desc, direction
    color = FR_COLORS.get(obj.color, obj.color)
    shape = FR_SHAPES.get(obj.shape, obj.shape)
    desc = f"Une forme géométrique, un {shape} {color}, est visible sur un fond neutre."
    if direction in FR_DIRECTIONS:
        phrase = FR_DIRECTIONS[direction]
        desc += f" Elle {phrase}." if direction == "still" else f" Elle se déplace {phrase}."
    else:
        desc += " Son mouvement est difficile à déterminer."
    return desc, direction


def describe_ai_captions(captions: list[str], scene_motion: float) -> str:
    """Summarize only the model's own frame-level observations. No external LLM."""
    normalized = []
    for raw in captions:
        cleaned = re.sub(r"\s+", " ", raw.strip().rstrip(". "))
        if cleaned and cleaned.lower() not in [x.lower() for x in normalized]:
            normalized.append(cleaned)
    if not normalized:
        return "The vision-language model returned no usable visual description."
    selected = normalized[:3]
    if len(selected) == 1:
        text = selected[0][0].upper() + selected[0][1:] + "."
    elif len(selected) == 2:
        text = f"At the beginning, {selected[0][0].lower() + selected[0][1:]}. Later, {selected[1][0].lower() + selected[1][1:]}."
    else:
        text = (f"At the beginning, {selected[0][0].lower() + selected[0][1:]}. "
                f"Later, {selected[1][0].lower() + selected[1][1:]}. "
                f"Toward the end, {selected[2][0].lower() + selected[2][1:]}.")
    if scene_motion >= 14:
        text += " Visual changes are noticeable between sampled frames."
    return text


def srt_from_captions(captions: list[str], timestamps: list[float], duration: float) -> str:
    def stamp(seconds: float) -> str:
        ms = max(0, round(seconds * 1000))
        hh, rem = divmod(ms, 3_600_000)
        mm, rem = divmod(rem, 60_000)
        ss, rest = divmod(rem, 1000)
        return f"{hh:02d}:{mm:02d}:{ss:02d},{rest:03d}"

    entries = []
    for i, (caption, start) in enumerate(zip(captions, timestamps)):
        end = timestamps[i+1] if i+1 < len(timestamps) else duration
        end = max(end, start + 0.001)
        entries.append(f"{i+1}\n{stamp(start)} --> {stamp(end)}\n{caption}\n")
    return "\n".join(entries) + "\n"
