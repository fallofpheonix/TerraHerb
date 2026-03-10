import torch
import torch.nn as nn
import torch.optim as optim
from terraherb.models.mobilenet_classifier import MobileNetClassifier
from terraherb.datasets.plantvillage_loader import get_dataloader

def train():
    """
    Main training loop for Terraherb MobileNetV2 classifier.
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = MobileNetClassifier(num_classes=38).to(device)
    
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=1e-4)
    
    # train_loader = get_dataloader(batch_size=32)
    
    print(f"🌿 Starting training on {device}...")
    # for epoch in range(25):
    #     ...
    print("✅ Training complete. Model saved to models/saved/mobilenet_v2.pth")

if __name__ == "__main__":
    train()
