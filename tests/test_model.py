from __future__ import annotations

import torch

from terraherb.models.mobilenet_classifier import MobileNetClassifier


def test_model_output_shape() -> None:
    model = MobileNetClassifier(num_classes=38, pretrained=False)
    out = model(torch.randn(1, 3, 224, 224))
    assert tuple(out.shape) == (1, 38)


def test_model_outputs_log_softmax_distribution() -> None:
    model = MobileNetClassifier(num_classes=38, pretrained=False)
    out = model(torch.randn(2, 3, 224, 224))
    probs = out.exp()
    assert torch.allclose(probs.sum(dim=1), torch.ones(2), atol=1e-4)


def test_backbone_freeze_and_head_trainable() -> None:
    model = MobileNetClassifier(pretrained=False, freeze_backbone=True)
    assert any(not p.requires_grad for p in model.features.parameters())
    assert any(p.requires_grad for p in model.classifier.parameters())


def test_save_and_load_roundtrip(tmp_path) -> None:
    model = MobileNetClassifier(pretrained=False)
    path = tmp_path / "mobilenet_v2.pth"
    model.save(str(path))
    loaded = MobileNetClassifier.from_pretrained(str(path), pretrained=False)
    assert loaded.num_classes == model.num_classes


def test_unfreeze_top_layers_increases_trainable_count() -> None:
    model = MobileNetClassifier(pretrained=False, freeze_backbone=True)
    before = model.count_parameters()["trainable"]
    model.unfreeze_top_layers(5)
    after = model.count_parameters()["trainable"]
    assert after > before
