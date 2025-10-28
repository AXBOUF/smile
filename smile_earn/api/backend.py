from flask import Flask, request, jsonify, render_template
import os, json
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify
import cv2, os, time, json
from datetime import datetime
from flask_cors import CORS
import face_recognition
import numpy as np
import pickle
import time, random

app = Flask(__name__)
@app.route('/')
def home():
    return render_template('home.html')

CORS(app)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CAPTURE_DIR = os.path.join(BASE_DIR, 'data', 'captures')
os.makedirs(CAPTURE_DIR, exist_ok=True)
DATASET_DIR = os.path.join(os.path.dirname(__file__), '../data/dataset')
os.makedirs(DATASET_DIR, exist_ok=True)
DB_FILE = os.path.join(BASE_DIR, 'data', 'db.json')
# Adjust to your working device (Brio often exposes /dev/video2 or /dev/video3)
CAPTURE_DEVICE = "/dev/video0"
def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, 'r') as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def capture_frame(device):
    cap = cv2.VideoCapture(device, cv2.CAP_V4L2)  # force V4L2 on Linux
    # reasonable defaults for Brio 100
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)

    time.sleep(2.5)  # warm-up

    ret, frame = cap.read()
    # retry a few times in case first frame is empty
    for _ in range(3):
        if ret and frame is not None:
            break
        time.sleep(0.5)
        ret, frame = cap.read()

    cap.release()
    if not ret or frame is None:
        raise RuntimeError("Failed to grab frame from camera")
    return frame

from face_reco import recognize_face

@app.route("/capture", methods=["POST"])
def capture_and_identify():
    frame = capture_frame(CAPTURE_DEVICE)
    name = recognize_face(frame)["person"]
    return jsonify({"status": "recognized", "person": name})

@app.route('/upload', methods=['POST'])
def upload_backend():
    name = request.form.get('name', '').strip()
    image = request.files.get('image')

    db = load_db()
    if name in db:
        pass  # user already exists, do nothing
    else:
        random_points = random.randint(0, 1000)
        db[name] = {"points": random_points}
        save_db(db)

    if not name or not image:
        return jsonify({"error": "Missing name or image"}), 400

    user_folder = os.path.join(DATASET_DIR, name)
    os.makedirs(user_folder, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = secure_filename(f"{name}_{timestamp}.jpg")
    save_path = os.path.join(user_folder, filename)
    image.save(save_path)


    return jsonify({
        "status": "success",
        "message": f"Image saved for {name}",
        "path": os.path.relpath(save_path, start=os.path.dirname(__file__)),
        "points": db[name]["points"]
    })




@app.route("/train", methods=["POST"])
def train_faces():
    from train_model import train_all_faces   # your function
    result = train_all_faces()
    return jsonify(result)

# train model route for convenience
from train_model import train_all_faces
@app.route("/train", methods=["GET"])
def train_faces_get():
    result = train_all_faces()
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
