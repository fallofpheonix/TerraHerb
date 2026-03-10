# Model

## PyTorch Path (Primary)
- Backbone: MobileNetV2
- Head: Linear(1280->512)->ReLU->Dropout->Linear(512->38)
- Output: log-softmax
- Loss: NLLLoss
- Optimizer: AdamW

## Training
- Two-phase schedule:
1. Head-only training (backbone frozen)
2. Fine-tune top backbone layers with lower LR
- Scheduler: CosineAnnealingLR
- Early stopping on validation accuracy

## TensorFlow Path (Strategy 98)
- Backbone: EfficientNetB0
- Stage 1: frozen backbone, train classifier head
- Stage 2: unfreeze top layers, low-LR fine-tuning
- Goal: improve top-1 accuracy toward 97-98%

## Metrics
- Top-1 Accuracy
- Top-5 Accuracy
- Validation loss
- Inference latency

## Artifacts
- PyTorch weights: `models/saved/mobilenet_v2*.pth`
- TensorFlow model: `models/saved/plant_disease_model_strat98.h5`
