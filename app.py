import os
import torch
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
from torchvision import transforms
from facenet_pytorch import MTCNN
from ai.models.model import DeepfakeDetector

app = Flask(__name__, template_folder='frontend', static_folder='frontend')

UPLOAD_FOLDER = 'assets/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- AI MODEL INITIALIZATION ---
device = torch.device("cpu")
checkpoint_path = "ai/checkpoints/best_model.pth"
mtcnn = MTCNN(keep_all=False, select_largest=True, post_process=False, device='cpu')

def load_trained_model():
    model = DeepfakeDetector(pretrained=False).to(device)
    checkpoint = torch.load(checkpoint_path, map_location=device)
    if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
        model.load_state_dict(checkpoint["model_state_dict"])
    else:
        model.load_state_dict(checkpoint)
    model.eval()
    return model

# Load model once when server starts
model = load_trained_model()

def crop_face(image_path):
    try:
        raw_img = Image.open(image_path).convert("RGB")
        boxes, _ = mtcnn.detect(raw_img)
        
        if boxes is not None and len(boxes) > 0:
            box = boxes[0]
            width, height = raw_img.size
            margin_x = (box[2] - box[0]) * 0.10
            margin_y = (box[3] - box[1]) * 0.10
            x1 = max(0, int(box[0] - margin_x))
            y1 = max(0, int(box[1] - margin_y))
            x2 = min(width, int(box[2] + margin_x))
            y2 = min(height, int(box[3] + margin_y))
            
            cropped = raw_img.crop((x1, y1, x2, y2))
            # Save debug crop so you can inspect what the model actually sees
            cropped.save("assets/debug_cropped.jpg")
            return cropped
        else:
            raw_img.save("assets/debug_cropped.jpg")
            return raw_img
    except Exception:
        fallback = Image.open(image_path).convert("RGB")
        fallback.save("assets/debug_cropped.jpg")
        return fallback

def predict_deepfake(image_path):
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    image = crop_face(image_path)
    tensor = transform(image).unsqueeze(0).to(device)
    
    with torch.no_grad():
        outputs = model(tensor)
        probabilities = torch.softmax(outputs, dim=1)
        confidence, predicted_class = torch.max(probabilities, 1)
        
    classes = ['Fake', 'Real']
    label = classes[predicted_class.item()]
    conf_percentage = confidence.item() * 100
    is_fake = (label == 'Fake')
    
    return {
        "is_fake": is_fake,
        "confidence": f"{conf_percentage:.2f}%",
        "details": f"Model prediction: {label} (Fake: {probabilities[0][0]*100:.1f}%, Real: {probabilities[0][1]*100:.1f}%)"
    }

@app.route('/')
def home():
    return render_template('analyze.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file part provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            result = predict_deepfake(filepath)
            return jsonify({
                "status": "success",
                "filename": filename,
                "is_fake": result["is_fake"],
                "confidence": result["confidence"],
                "details": result["details"]
            })
        except Exception as e:
            return jsonify({"error": f"Model inference failed: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)