import torch
import torch.nn as nn
from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights

class DeepfakeDetector(nn.Module):
    def __init__(self, pretrained=True, dropout_rate=0.3):
        super(DeepfakeDetector, self).__init__()
        if pretrained:
            weights = EfficientNet_B0_Weights.DEFAULT
            self.model = efficientnet_b0(weights=weights)
        else:
            self.model = efficientnet_b0(weights=None)
        in_features = self.model.classifier[1].in_features
        self.model.classifier = nn.Sequential(
            nn.Dropout(p=dropout_rate),
            nn.Linear(in_features, 2)  # Output: 2 classes (Fake, Real)
        )
    def forward(self, x):
        return self.model(x)
def get_model(device="cuda" if torch.cuda.is_available() else "cpu"):
    model = DeepfakeDetector(pretrained=True)
    model = model.to(device)
    return model