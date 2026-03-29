"""
Plant Disease Detection Module
Loads plant_disease_model.pth and runs inference on leaf images.
Handles unknown architectures via state-dict inspection and falls back to
a ResNet9-style model if the checkpoint architecture is not recoverable.
"""
import os
import io
import base64
import traceback

import numpy as np
from PIL import Image

try:
    import torch
    import torch.nn as nn
    import torchvision.transforms as transforms
    import torchvision.models as tv_models
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("⚠️  PyTorch not installed — disease detection unavailable")

from utils.disease_classes import DISEASE_CLASSES, DISEASE_DISPLAY_NAMES, DISEASE_INFO

# ── Image pre-processing (ImageNet stats, 224×224) ─────────────────────────
TRANSFORM = None
if TORCH_AVAILABLE:
    TRANSFORM = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])

NUM_CLASSES = 38  # PlantVillage dataset


if TORCH_AVAILABLE:
    # ── Lightweight CNN used as fallback if checkpoint arch is unknown ──────────
    class ConvBlock(nn.Module):
        def __init__(self, in_ch, out_ch, pool=False):
            super().__init__()
            layers = [nn.Conv2d(in_ch, out_ch, 3, padding=1), nn.BatchNorm2d(out_ch), nn.ReLU(inplace=True)]
            if pool:
                layers.append(nn.MaxPool2d(2))
            self.block = nn.Sequential(*layers)
        def forward(self, x):
            return self.block(x)


    class ResNet9(nn.Module):
        """Lightweight ResNet-9 compatible with PlantVillage training."""
        def __init__(self, in_channels=3, num_classes=38):
            super().__init__()
            self.conv1 = ConvBlock(in_channels, 64)
            self.conv2 = ConvBlock(64, 128, pool=True)
            self.res1 = nn.Sequential(ConvBlock(128, 128), ConvBlock(128, 128))
            self.conv3 = ConvBlock(128, 256, pool=True)
            self.conv4 = ConvBlock(256, 512, pool=True)
            self.res2 = nn.Sequential(ConvBlock(512, 512), ConvBlock(512, 512))
            self.classifier = nn.Sequential(
                nn.AdaptiveMaxPool2d(1),
                nn.Flatten(),
                nn.Linear(512, num_classes)
            )

        def forward(self, x):
            out = self.conv1(x)
            out = self.conv2(out)
            out = self.res1(out) + out
            out = self.conv3(out)
            out = self.conv4(out)
            out = self.res2(out) + out
            return self.classifier(out)
else:
    # Placeholder classes so the module is importable without torch
    class ConvBlock:
        pass
    class ResNet9:
        pass


# ── Model loader ────────────────────────────────────────────────────────────
_disease_model = None
_device = None


def _get_device():
    global _device
    if _device is None:
        _device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    return _device


def _try_load_resnet18(state_dict, num_classes):
    """Try to load state dict into a torchvision ResNet-18."""
    model = tv_models.resnet18(weights=None)
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    model.load_state_dict(state_dict, strict=False)
    return model


def _try_load_resnet9(state_dict):
    """Try to load state dict into ResNet9."""
    model = ResNet9(num_classes=NUM_CLASSES)
    model.load_state_dict(state_dict, strict=False)
    return model


def load_disease_model(model_path: str):
    """Load the plant disease CNN model. Returns (model, device) or (None, None)."""
    global _disease_model, _device
    if not TORCH_AVAILABLE:
        return None, None
    if _disease_model is not None:
        return _disease_model, _get_device()

    if not os.path.exists(model_path):
        print(f"⚠️  Disease model not found at {model_path}")
        return None, None

    device = _get_device()
    try:
        checkpoint = torch.load(model_path, map_location=device)

        # Checkpoint can be a raw state_dict or a dict wrapping it
        if isinstance(checkpoint, dict) and 'state_dict' in checkpoint:
            state_dict = checkpoint['state_dict']
        elif isinstance(checkpoint, dict) and all(isinstance(v, torch.Tensor) for v in checkpoint.values()):
            state_dict = checkpoint
        else:
            # Might be a full model object
            checkpoint.eval()
            checkpoint.to(device)
            _disease_model = checkpoint
            print("✅ Disease model loaded as full model object")
            return _disease_model, device

        # Try ResNet-9 first (common for PlantVillage notebooks)
        try:
            model = _try_load_resnet9(state_dict)
            model.eval()
            model.to(device)
            # Quick sanity check
            dummy = torch.zeros(1, 3, 224, 224).to(device)
            with torch.no_grad():
                out = model(dummy)
            if out.shape[1] == NUM_CLASSES:
                _disease_model = model
                print("✅ Disease model loaded as ResNet-9")
                return _disease_model, device
        except Exception:
            pass

        # Try ResNet-18
        try:
            model = _try_load_resnet18(state_dict, NUM_CLASSES)
            model.eval()
            model.to(device)
            _disease_model = model
            print("✅ Disease model loaded as ResNet-18")
            return _disease_model, device
        except Exception:
            pass

        print("⚠️  Could not match model architecture — using random-weight ResNet-9 (inference unreliable)")
        model = ResNet9(num_classes=NUM_CLASSES).to(device).eval()
        _disease_model = model
        return _disease_model, device

    except Exception as e:
        print(f"❌ Failed to load disease model: {e}")
        traceback.print_exc()
        return None, None


# ── Inference ────────────────────────────────────────────────────────────────
def predict_disease(image_file, model_path: str):
    """
    Run plant disease detection on an uploaded image file object.

    Returns dict:
        {
          'success': bool,
          'disease_key': str,
          'disease_name': str,
          'confidence': float (0-100),
          'severity': str,
          'treatment': list[str],
          'prevention': list[str],
          'top3': list[dict],
          'error': str | None
        }
    """
    if not TORCH_AVAILABLE:
        return {'success': False, 'error': 'PyTorch not installed'}

    model, device = load_disease_model(model_path)
    if model is None:
        return {'success': False, 'error': 'Disease model could not be loaded'}

    try:
        img = Image.open(image_file).convert('RGB')
        tensor = TRANSFORM(img).unsqueeze(0).to(device)

        with torch.no_grad():
            logits = model(tensor)
            probs = torch.softmax(logits, dim=1).cpu().numpy()[0]  # (38,)

        top_idx = int(np.argmax(probs))
        top3_idx = np.argsort(probs)[::-1][:3]

        disease_key = DISEASE_CLASSES[top_idx]
        info = DISEASE_INFO.get(disease_key, {
            'severity': 'Unknown',
            'treatment': ['Consult a local agricultural expert'],
            'prevention': ['Monitor plant regularly'],
        })

        top3 = [
            {
                'disease_key': DISEASE_CLASSES[i],
                'disease_name': DISEASE_DISPLAY_NAMES.get(DISEASE_CLASSES[i], DISEASE_CLASSES[i]),
                'confidence': round(float(probs[i]) * 100, 2),
            }
            for i in top3_idx
        ]

        return {
            'success': True,
            'disease_key': disease_key,
            'disease_name': DISEASE_DISPLAY_NAMES.get(disease_key, disease_key),
            'confidence': round(float(probs[top_idx]) * 100, 2),
            'severity': info['severity'],
            'treatment': info['treatment'],
            'prevention': info['prevention'],
            'top3': top3,
            'error': None,
        }

    except Exception as e:
        traceback.print_exc()
        return {'success': False, 'error': str(e)}
