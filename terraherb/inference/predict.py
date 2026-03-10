import torch
from terraherb.models.mobilenet_classifier import MobileNetClassifier
import torchvision.transforms as transforms
from PIL import Image
import io

class PlantPredictor:
    def __init__(self, model_path: str = "models/saved/mobilenet_v2.pth"):
        self.model = MobileNetClassifier()
        # In a real scenario, we would load the weights here
        # self.model.load_state_dict(torch.load(model_path))
        self.model.eval()
        
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

    def predict(self, image_bytes: bytes) -> str:
        # img = Image.open(io.BytesIO(image_bytes))
        # with torch.no_grad():
        #     output = self.model(self.transform(img).unsqueeze(0))
        return "Ocimum tenuiflorum" # Tulsi
