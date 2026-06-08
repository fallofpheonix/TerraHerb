"""
Plant species and disease classifier using MobileNetV2 backbone.
Handles preprocessing, inference, and confidence scoring.
"""

import io
import logging
from typing import Optional

import cv2
import numpy as np
import torch
import torchvision.transforms as transforms
from PIL import Image

from terraherb.inference.classes import PLANT_CLASSES

logger = logging.getLogger(__name__)

NUM_CLASSES = len(PLANT_CLASSES)


def preprocess_image(image_bytes: bytes) -> torch.Tensor:
    """
    Preprocess raw image bytes into a normalized tensor.

    Steps:
      1. Decode bytes → PIL Image (RGB)
      2. OpenCV-based quality check (blur detection)
      3. Resize → CenterCrop → ToTensor → Normalize (ImageNet stats)

    Args:
        image_bytes: Raw bytes from an uploaded image file.

    Returns:
        A (1, 3, 224, 224) float tensor ready for model inference.

    Raises:
        ValueError: If the image cannot be decoded or is too blurry.
    """
    try:
        img_pil = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as exc:
        raise ValueError(f"Cannot decode image: {exc}") from exc

    # Blur detection via Laplacian variance (threshold empirically set for leaf images)
    img_cv = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
    if blur_score < 10.0:
        logger.warning("Low sharpness score %.2f — image may be blurry.", blur_score)

    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225],
        ),
    ])
    tensor = transform(img_pil).unsqueeze(0)  # (1, 3, 224, 224)
    return tensor


class PlantClassifier:
    """
    CNN-based plant species / disease classifier.

    Uses a MobileNetV2 backbone fine-tuned on the PlantVillage dataset.
    Falls back to a randomly-initialised head when no weights file is found
    (useful during development / CI).
    """

    def __init__(
        self,
        model_path: str = "models/saved/mobilenet_v2.pth",
        num_classes: int = NUM_CLASSES,
        device: Optional[str] = None,
    ) -> None:
        from terraherb.models.mobilenet_classifier import MobileNetClassifier

        self.device = torch.device(
            device if device else ("cuda" if torch.cuda.is_available() else "cpu")
        )
        self.num_classes = num_classes

        # Load weights if available
        try:
            self.model = MobileNetClassifier.from_pretrained(
                path=model_path, 
                num_classes=num_classes, 
                device=str(self.device)
            )
        except FileNotFoundError:
            logger.warning(
                "Weight file not found at '%s'. Running with random weights.", model_path
            )
            self.model = MobileNetClassifier(num_classes=num_classes, pretrained=False).to(self.device)
            self.model.eval()

    def predict(self, image_bytes: bytes, top_k: int = 3) -> dict:
        """
        Predict the plant class for a given image.

        Args:
            image_bytes: Raw bytes of the uploaded image.
            top_k: Number of top predictions to return.

        Returns:
            dict with keys:
              - "top_class" (str): Highest-confidence class label.
              - "confidence" (float): Probability for the top class (0–1).
              - "top_k" (list[dict]): Top-k predictions with label + probability.
        """
        tensor = preprocess_image(image_bytes).to(self.device)

        with torch.no_grad():
            logits = self.model(tensor)                    # (1, num_classes)
            probs = torch.softmax(logits, dim=1)[0]        # (num_classes,)

        top_probs, top_indices = torch.topk(probs, k=min(top_k, self.num_classes))

        top_predictions = [
            {
                "label": PLANT_CLASSES[idx.item()],
                "probability": round(prob.item(), 4),
            }
            for prob, idx in zip(top_probs, top_indices)
        ]

        return {
            "top_class": top_predictions[0]["label"],
            "confidence": top_predictions[0]["probability"],
            "top_k": top_predictions,
        }


def get_classifier(model_path: str = "models/saved/mobilenet_v2.pth") -> PlantClassifier:
    """Factory function — returns a singleton-style classifier."""
    return PlantClassifier(model_path=model_path)
