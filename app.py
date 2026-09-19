import os
import torch
from dotenv import load_dotenv
load_dotenv()
from flask import Flask, render_template, request, jsonify, send_file, session
from werkzeug.utils import secure_filename
from PIL import Image
from torchvision import transforms
from facenet_pytorch import MTCNN
from backend.report_generator import generate_report
from backend.image_uploader import upload_image

from ai.models.model import DeepfakeDetector
from backend.reverse_search import analyze_reverse_search
from backend.auth import (
    register_user,
    authenticate_user,
    log_activity,
    get_connection,
    get_user_id_by_login,
    update_user_profile,
    change_user_password,
    DatabaseUnavailableError
)

app = Flask(__name__, template_folder='frontend', static_folder='frontend')
app.secret_key = os.getenv("FLASK_SECRET_KEY", "deepguard-dev-key")

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No registration data provided"}), 400

    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not username or not email or not password:
        return jsonify({"error": "All fields are required"}), 400

    try:
        success, message = register_user(username, email, password)

        if success:
            return jsonify({
                "status": "success",
                "message": message
            }), 201

        return jsonify({
            "status": "error",
            "message": message
        }), 409

    except DatabaseUnavailableError:
        return jsonify({
            "status": "error",
            "message": "Database is temporarily unavailable. Please try again later."
        }), 503

@app.route('/api/login', methods=['POST'])
def login():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "No login data provided"
        }), 400

    login = data.get("login", "").strip()
    password = data.get("password", "")

    if not login or not password:
        return jsonify({
            "status": "error",
            "message": "Username/email and password are required"
        }), 400

    try:

        user = authenticate_user(
            login,
            password
        )

    except DatabaseUnavailableError:

        return jsonify({
            "status": "error",
            "message":
                "Database is temporarily unavailable. Please try again later."
        }), 503

    if not user:

        return jsonify({
            "status": "error",
            "message": "Invalid email or password"
        }), 401

    session["user_id"] = user["user_id"]

    log_activity(
        user["user_id"],
        "User logged in"
    )

    return jsonify({
        "status": "success",
        "message": "Login successful",
        "user": {
            "user_id": user["user_id"],
            "username": user["username"],
            "email": user["email"]
        }
    })
UPLOAD_FOLDER = 'assets/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ==============================
# AI MODEL INITIALIZATION
# ==============================

device = torch.device("cpu")

checkpoint_path = "ai/checkpoints/best_model.pth"


mtcnn = MTCNN(
    keep_all=False,
    select_largest=True,
    post_process=False,
    device='cpu'
)


def load_trained_model():

    model = DeepfakeDetector(
        pretrained=False
    ).to(device)


    checkpoint = torch.load(
        checkpoint_path,
        map_location=device
    )


    if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
        model.load_state_dict(
            checkpoint["model_state_dict"]
        )

    else:
        model.load_state_dict(checkpoint)


    model.eval()

    return model



# Load model once
model = load_trained_model()



# ==============================
# FACE CROPPING
# ==============================

def crop_face(image_path):

    try:

        raw_img = Image.open(
            image_path
        ).convert("RGB")


        boxes, _ = mtcnn.detect(raw_img)


        if boxes is not None and len(boxes) > 0:

            box = boxes[0]


            width, height = raw_img.size


            margin_x = (box[2] - box[0]) * 0.10
            margin_y = (box[3] - box[1]) * 0.10


            x1 = max(
                0,
                int(box[0] - margin_x)
            )

            y1 = max(
                0,
                int(box[1] - margin_y)
            )


            x2 = min(
                width,
                int(box[2] + margin_x)
            )


            y2 = min(
                height,
                int(box[3] + margin_y)
            )


            cropped = raw_img.crop(
                (x1, y1, x2, y2)
            )


            cropped.save(
                "assets/debug_cropped.jpg"
            )


            return cropped


        else:

            raw_img.save(
                "assets/debug_cropped.jpg"
            )

            return raw_img



    except Exception:


        fallback = Image.open(
            image_path
        ).convert("RGB")


        fallback.save(
            "assets/debug_cropped.jpg"
        )


        return fallback




# ==============================
# DEEPFAKE PREDICTION
# ==============================

def predict_deepfake(image_path):


    transform = transforms.Compose([

        transforms.Resize(
            (224,224)
        ),

        transforms.ToTensor(),

        transforms.Normalize(
            mean=[
                0.485,
                0.456,
                0.406
            ],

            std=[
                0.229,
                0.224,
                0.225
            ]
        )

    ])



    image = crop_face(
        image_path
    )


    tensor = transform(
        image
    ).unsqueeze(0).to(device)



    with torch.no_grad():

        outputs = model(
            tensor
        )


        probabilities = torch.softmax(
            outputs,
            dim=1
        )


        confidence, predicted_class = torch.max(
            probabilities,
            1
        )



    classes = [
        "Fake",
        "Real"
    ]


    label = classes[
        predicted_class.item()
    ]


    conf_percentage = confidence.item() * 100


    is_fake = (
        label == "Fake"
    )



    return {

        "is_fake": is_fake,

        "confidence":
            f"{conf_percentage:.2f}%",


        "details":
            f"Model prediction: {label} "
            f"(Fake: {probabilities[0][0]*100:.1f}%, "
            f"Real: {probabilities[0][1]*100:.1f}%)"

    }




# ==============================
# ROUTES
# ==============================


@app.route('/')
def home():

    return render_template(
        'homepage/login.html'
    )



# ------------------------------
# Deepfake Detection API
# ------------------------------

@app.route(
    '/api/analyze',
    methods=['POST']
)
def analyze_image():

    if 'file' not in request.files:

        return jsonify({
            "error":
            "No file part provided"
        }), 400

    file = request.files['file']

    if file.filename == '':

        return jsonify({
            "error":
            "No selected file"
        }), 400

    filename = secure_filename(
        file.filename
    )

    filepath = os.path.join(
        app.config['UPLOAD_FOLDER'],
        filename
    )
    file.save(
        filepath
    )
    user_id = session.get("user_id")

    if user_id:
        log_activity(user_id, "Image uploaded")
    try:

        # ==============================
        # AI DEEPFAKE ANALYSIS
        # ==============================

        result = predict_deepfake(
            filepath
        )

        if user_id:
            log_activity(
                user_id,
                "Image analyzed"
            )

        # ==============================
        # UPLOAD IMAGE TO IMGBB
        # ==============================

        image_url = upload_image(
            filepath
        )


        # ==============================
        # REVERSE IMAGE SEARCH
        # ==============================

        reverse_result = {
            "matches_found": 0,
            "digital_footprint": "UNAVAILABLE",
            "sources": []
        }


        if image_url:

            try:
                reverse_result = analyze_reverse_search(
                    image_url
                )

                if user_id:
                    log_activity(
                        user_id,
                        "Reverse image search completed"
                    )

            except Exception:

                if user_id:
                    log_activity(
                        user_id,
                        "Reverse image search failed"
                    )

                raise

        # ==============================
        # RETURN COMPLETE RESULT
        # ==============================

        return jsonify({

            "status":
            "success",

            "filename":
            filename,

            "is_fake":
            result["is_fake"],

            "confidence":
            result["confidence"],

            "details":
            result["details"],

            "reverse_search":
            reverse_result

        })


    except Exception as e:

        if user_id:
            log_activity(user_id, "Analysis failed")

        return jsonify({

            "error":
            f"Analysis failed: {str(e)}"

        }), 500

@app.route('/api/activity', methods=['GET'])
def get_activity():

    user_id = session.get("user_id")

    if not user_id:
        return jsonify({
            "error": "User not logged in"
        }), 401

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT activity_id, action, created_at
            FROM activity_log
            WHERE user_id = %s
            ORDER BY created_at DESC, activity_id DESC
        """

        cursor.execute(
            query,
            (user_id,)
        )

        activities = cursor.fetchall()

        for activity in activities:

            if activity["created_at"]:

                activity["created_at"] = activity["created_at"].strftime(
                    "%Y-%m-%dT%H:%M:%S"
                )

        return jsonify({
            "status": "success",
            "activities": activities
        })

    except DatabaseUnavailableError:

        return jsonify({
            "status": "error",
            "message": "Database is temporarily unavailable. Please try again later."
        }), 503

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": "Unable to load activity history."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()

@app.route('/api/report', methods=['POST'])
def generate_analysis_report():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "No analysis data provided."
        }), 400

    try:

        report_path = generate_report(
            filename=data.get("filename", "Unknown"),
            is_fake=data.get("is_fake", False),
            confidence=data.get("confidence", "Unknown"),
            details=data.get("details", "No details available."),
            reverse_search=data.get("reverse_search")
        )

        user_id = session.get("user_id")

        if user_id:
            log_activity(
                user_id,
                "Analysis report generated"
            )

            log_activity(
                user_id,
                "Report downloaded"
            )

        return send_file(
            report_path,
            as_attachment=True,
            download_name="DeepGuard_Analysis_Report.pdf"
        )

    except Exception as e:

        user_id = session.get("user_id")

        if user_id:
            log_activity(
                user_id,
                "Report generation failed"
            )

        return jsonify({
            "error": str(e)
        }), 500



# ------------------------------
# Reverse Image Search API
# ------------------------------

@app.route(
    '/api/reverse-search',
    methods=['POST']
)

def reverse_search_image():


    if 'image_url' not in request.form:

        return jsonify({

            "error":
            "Image URL missing"

        }),400



    image_url = request.form[
        'image_url'
    ]



    try:


        result = analyze_reverse_search(
            image_url
        )



        return jsonify({

            "status":
            "success",


            "reverse_search":
            result

        })



    except Exception as e:


        return jsonify({

            "error":
            f"Reverse search failed: {str(e)}"

        }),500




# ==============================
# RUN SERVER
# ==============================

if __name__ == '__main__':

    app.run(
        debug=True,
        port=5000
    )