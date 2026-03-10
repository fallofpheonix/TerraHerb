"""
MobileNetV2-based plant classifier model definition.

Architecture:
  - Backbone: MobileNetV2 (ImageNet pre-trained, backbone frozen by default)
  - Head: Linear(1280 → 512) → ReLU → Dropout(0.2) → Linear(512 → num_classes)
  - Output: Log-softmax probabilities (use NLLLoss during training)

Usage:
    model = MobileNetClassifier(num_classes=38, freeze_backbone=True)
    # During training, load with:
    #   model = MobileNetClassifier.from_pretrained("models/saved/mobilenet_v2.pth")
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import torch
import torch.nn as nn
import torchvision.models as models

logger = logging.getLogger(__name__)


class MobileNetClassifier(nn.Module):
    """
    Transfer-learning classifier built on MobileNetV2.

    Args:
        num_classes: Number of output classes (default 38 for PlantVillage).
        freeze_backbone: If True, backbone weights are frozen (feature extraction mode).
                         Set False for full fine-tuning.
        dropout: Dropout probability in the classification head.
        pretrained: Whether to initialise the backbone with ImageNet weights.
    """

    def __init__(
        self,
        num_classes: int = 38,
        freeze_backbone: bool = True,
        dropout: float = 0.2,
        pretrained: bool = True,
    ) -> None:
        super().__init__()
        self.num_classes = num_classes

        # Load MobileNetV2 backbone
        weights = models.MobileNet_V2_Weights.IMAGENET1K_V1 if pretrained else None
        backbone = models.mobilenet_v2(weights=weights)

        # Freeze backbone parameters (feature extraction mode)
        if freeze_backbone:
            for param in backbone.features.parameters():
                param.requires_grad = False

        self.features = backbone.features          # (B, 1280, 7, 7) after pooling
        self.pool = nn.AdaptiveAvgPool2d((1, 1))   # (B, 1280, 1, 1)

        last_channel = backbone.last_channel       # 1280

        # Custom classification head
        self.classifier = nn.Sequential(
            nn.Dropout(p=dropout),
            nn.Linear(last_channel, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(p=dropout),
            nn.Linear(512, num_classes),
        )

        # Initialise head weights
        self._init_head()

    def _init_head(self) -> None:
        """Kaiming initialisation for Linear layers in the head."""
        for module in self.classifier.modules():
            if isinstance(module, nn.Linear):
                nn.init.kaiming_normal_(module.weight, mode="fan_out", nonlinearity="relu")
                if module.bias is not None:
                    nn.init.zeros_(module.bias)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.

        Args:
            x: Input tensor of shape (B, 3, 224, 224).

        Returns:
            Log-softmax logits of shape (B, num_classes).
        """
        x = self.features(x)          # (B, 1280, 7, 7)
        x = self.pool(x)              # (B, 1280, 1, 1)
        x = torch.flatten(x, 1)       # (B, 1280)
        x = self.classifier(x)        # (B, num_classes)
        return torch.log_softmax(x, dim=1)

    def unfreeze_top_layers(self, n_layers: int = 5) -> None:
        """
        Unfreeze the last `n_layers` convolutional blocks for fine-tuning.
        Called after initial head-only training to enable deeper adaptation.
        """
        all_layers = list(self.features.children())
        for layer in all_layers[-n_layers:]:
            for param in layer.parameters():
                param.requires_grad = True
        trainable = sum(p.numel() for p in self.parameters() if p.requires_grad)
        logger.info("Unfroze last %d layers. Trainable params: %d", n_layers, trainable)

    def save(self, path: str) -> None:
        """Save model state dict to disk."""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        torch.save(self.state_dict(), path)
        logger.info("Model saved to '%s'.", path)

    @classmethod
    def from_pretrained(
        cls,
        path: str,
        num_classes: int = 38,
        device: Optional[str] = None,
        **kwargs,
    ) -> "MobileNetClassifier":
        """
        Load a model from a saved state dict.

        Args:
            path: Path to the .pth file.
            num_classes: Must match the value used when saving.
            device: Target device (defaults to CUDA if available).
        """
        map_device = torch.device(
            device if device else ("cuda" if torch.cuda.is_available() else "cpu")
        )
        kwargs = dict(kwargs)
        kwargs.setdefault("pretrained", False)
        model = cls(num_classes=num_classes, **kwargs)
        state = torch.load(path, map_location=map_device, weights_only=True)
        model.load_state_dict(state)
        model.to(map_device)
        model.eval()
        logger.info("Loaded MobileNetClassifier from '%s' on %s.", path, map_device)
        return model

    def count_parameters(self) -> dict[str, int]:
        """Return trainable / total parameter counts."""
        total = sum(p.numel() for p in self.parameters())
        trainable = sum(p.numel() for p in self.parameters() if p.requires_grad)
        return {"total": total, "trainable": trainable, "frozen": total - trainable}
