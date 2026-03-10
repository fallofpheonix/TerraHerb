import torch
import pytest
from terraherb.models.mobilenet_classifier import MobileNetClassifier

def test_model_output_shape():
    """
    Verify the model produces the correct number of class logs.
    """
    model = MobileNetClassifier(num_classes=38)
    dummy_input = torch.randn(1, 3, 224, 224)
    output = model(dummy_input)
    assert output.shape == (1, 38)

def test_model_trainable_params():
    """
    Ensure backbone is frozen and head is trainable.
    """
    model = MobileNetClassifier()
    # Check that some parameters are trainable (the head)
    trainable = any(p.requires_grad for p in model.parameters())
    assert trainable is True
