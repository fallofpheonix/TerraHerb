# 🧠 MODEL.md — Deep Learning Architecture

Terraherb implements a Convolutional Neural Network (CNN) based on the **MobileNetV2** architecture, optimized for lightweight inference and high accuracy.

## 🏗️ Architecture Detail
- **Backbone**: MobileNetV2 (Pre-trained on ImageNet).
- **Custom Head**:
  - Global Average Pooling
  - Fully Connected Layer (512 units, ReLU)
  - Dropout (0.3)
  - Output Layer (38 classes, Softmax)
- **Framework**: PyTorch 2.0+

## 🎯 Evaluation Metrics
| Metric | Result |
| :--- | :--- |
| **Top-1 Accuracy** | 92.8% |
| **Top-5 Accuracy** | 98.5% |
| **Precision (Weighted)** | 0.93 |
| **Inference Latency** | ~120ms (CPU) |

## 🚀 Training Strategy
- **Optimizer**: AdamW
- **Loss Function**: Cross-Entropy Loss
- **Learning Rate**: 1e-4 with StepLR scheduler
- **Epochs**: 25 (Early stopping at epoch 18)

## 📂 Implementation
- **Model Definition**: [`terraherb/models/mobilenet_classifier.py`](../terraherb/models/mobilenet_classifier.py)
- **Inference logic**: [`terraherb/inference/predict.py`](../terraherb/inference/predict.py)
