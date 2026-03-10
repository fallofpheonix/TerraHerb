import torch.nn as nn
import torchvision.models as models

class MobileNetClassifier(nn.Module):
    def __init__(self, num_classes: int = 38):
        super(MobileNetClassifier, self).__init__()
        self.model = models.mobilenet_v2(pretrained=True)
        # Freeze backbone
        for param in self.model.parameters():
            param.requires_grad = False
        
        # Replace classifier
        self.model.classifier[1] = nn.Sequential(
            nn.Linear(self.model.last_channel, 512),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(512, num_classes),
            nn.LogSoftmax(dim=1)
        )

    def forward(self, x):
        return self.model(x)
