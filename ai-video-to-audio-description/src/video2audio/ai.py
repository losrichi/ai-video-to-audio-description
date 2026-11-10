"""Optional real-image captioning using pretrained Salesforce BLIP.

Weights are downloaded via Hugging Face on first use. This module is imported
only if --backend blip is selected. It is NOT necessary for the offline demo.
"""
import cv2
from PIL import Image


class BLIPCaptioner:
    MODEL_NAME = "Salesforce/blip-image-captioning-base"

    def __init__(self, device: str = "auto"):
        try:
            import torch
            from transformers import BlipProcessor, BlipForConditionalGeneration
        except ImportError as exc:
            raise RuntimeError("BLIP backend requires pip install -e '.[ai]'") from exc
        self.torch = torch
        self.device = ("cuda" if torch.cuda.is_available() else "cpu") if device == "auto" else device
        self.processor = BlipProcessor.from_pretrained(self.MODEL_NAME)
        self.model = BlipForConditionalGeneration.from_pretrained(self.MODEL_NAME).to(self.device).eval()

    def caption(self, frame_bgr) -> str:
        image = Image.fromarray(cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB))
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        with self.torch.inference_mode():
            tokens = self.model.generate(**inputs, max_new_tokens=40, num_beams=3)
        return self.processor.decode(tokens[0], skip_special_tokens=True).strip()
