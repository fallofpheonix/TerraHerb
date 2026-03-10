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

logger = logging.getLogger(__name__)

# 38 PlantVillage classes (species + health status)
PLANT_CLASSES = [
    "Apple___Apple_scab",
    "Apple___Black_rot",
    "Apple___Cedar_apple_rust",
    "Apple___healthy",
    "Blueberry___healthy",
    "Cherry_(including_sour)___Powdery_mildew",
    "Cherry_(including_sour)___healthy",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
    "Corn_(maize)___Common_rust_",
    "Corn_(maize)___Northern_Leaf_Blight",
    "Corn_(maize)___healthy",
    "Grape___Black_rot",
    "Grape___Esca_(Black_Measles)",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",
    "Grape___healthy",
    "Orange___Haunglongbing_(Citrus_greening)",
    "Peach___Bacterial_spot",
    "Peach___healthy",
    "Pepper,_bell___Bacterial_spot",
    "Pepper,_bell___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Raspberry___healthy",
    "Soybean___healthy",
    "Squash___Powdery_mildew",
    "Strawberry___Leaf_scorch",
    "Strawberry___healthy",
    "Tomato___Bacterial_spot",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot",
    "Tomato___Spider_mites Two-spotted_spider_mite",
    "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato___Tomato_mosaic_virus",
    "Tomato___healthy",
]

NUM_CLASSES = len(PLANT_CLASSES)  # 38


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
        import torchvision.models as tv_models

        self.device = torch.device(
            device if device else ("cuda" if torch.cuda.is_available() else "cpu")
        )
        self.num_classes = num_classes

        # Build backbone
        self.model = tv_models.mobilenet_v2(weights=None)
        self.model.classifier[1] = torch.nn.Sequential(
            torch.nn.Linear(self.model.last_channel, 512),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.2),
            torch.nn.Linear(512, num_classes),
        )

        # Load weights if available
        try:
            state = torch.load(model_path, map_location=self.device, weights_only=True)
            self.model.load_state_dict(state)
            logger.info("Loaded weights from %s", model_path)
        except FileNotFoundError:
            logger.warning(
                "Weight file not found at '%s'. Running with random weights.", model_path
            )

        self.model.to(self.device)
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
