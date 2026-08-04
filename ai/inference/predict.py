import sys
import torch
import torch.nn as nn
from PIL import Image
from torchvision import transforms
from facenet_pytorch import MTCNN

from ai.models.model import DeepfakeDetector

# Initialize MTCNN face detector
mtcnn = MTCNN(keep_all=False, select_largest=True, post_process=False, device='cpu')

def crop_face(image_path):
    """Detects and crops the primary face from an image. Returns full image if no face detected."""
    try:
        raw_img = Image.open(image_path).convert("RGB")
        
        # Detect face bounding box
        boxes, _ = mtcnn.detect(raw_img)
        
        if boxes is not None and len(boxes) > 0:
            box = boxes[0]
            # Add 10% margin padding around the face
            width, height = raw_img.size
            margin_x = (box[2] - box[0]) * 0.10
            margin_y = (box[3] - box[1]) * 0.10
            
            x1 = max(0, int(box[0] - margin_x))
            y1 = max(0, int(box[1] - margin_y))
            x2 = min(width, int(box[2] + margin_x))
            y2 = min(height, int(box[3] + margin_y))
            
            cropped_img = raw_img.crop((x1, y1, x2, y2))
            print("✂️ Face detected and cropped successfully using MTCNN.")
            return cropped_img
        else:
            print("⚠️ No face detected by MTCNN. Analyzing full image.")
            return raw_img
    except Exception as e:
        print(f"⚠️ Error during face cropping: {e}. Falling back to full image.")
        return Image.open(image_path).convert("RGB")

def load_trained_model(checkpoint_path, device):
    model = DeepfakeDetector(pretrained=False).to(device)
    checkpoint = torch.load(checkpoint_path, map_location=device)
    
    if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
        model.load_state_dict(checkpoint["model_state_dict"])
    else:
        model.load_state_dict(checkpoint)
        
    model.eval()
    return model

def predict_image(image_path, model, device):
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    # Preprocess with face cropping
    image = crop_face(image_path)
    tensor = transform(image).unsqueeze(0).to(device)
    
    with torch.no_grad():
        outputs = model(tensor)
        probabilities = torch.softmax(outputs, dim=1)
        confidence, predicted_class = torch.max(probabilities, 1)
        
    classes = ['Fake', 'Real']
    result_label = classes[predicted_class.item()]
    conf_percentage = confidence.item() * 100
    
    return result_label, conf_percentage, probabilities[0]

if __name__ == "__main__":
    device = torch.device("cpu")
    checkpoint_path = "ai/checkpoints/best_model.pth"
    
    if len(sys.argv) > 1:
        img_path = sys.argv[1]
    else:
        print("❌ Please provide an image path.")
        sys.exit(1)
        
    print(f"\n🔍 Analyzing image: {img_path}")
    
    try:
        model = load_trained_model(checkpoint_path, device)
        label, conf, probs = predict_image(img_path, model, device)
        
        print("\n--- Prediction Result ---")
        print(f"Result:     {label}")
        print(f"Confidence: {conf:.2f}%")
        print(f"Probabilities -> Fake: {probs[0]*100:.2f}% | Real: {probs[1]*100:.2f}%\n")
    except Exception as e:
        print(f"❌ Error during inference: {e}")