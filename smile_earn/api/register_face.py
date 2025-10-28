from flask import Flask, render_template, request, jsonify
import requests, random, os

app = Flask(__name__, template_folder='templates', static_folder='static')

# the backend endpoint that will actually save the file
BACKEND_URL = "http://127.0.0.1:5002/upload"  # change this if backend runs elsewhere

 # placeholder for any future database saving logic

@app.route('/')
def home():
    return render_template('register_face.html')
# while uploading create a db.json file in data/dataset to store user info


@app.route('/upload', methods=['POST'])
def upload_proxy():
    """Receive image + name from browser and forward to backend"""
    name = request.form.get('name', '').strip()
    image = request.files.get('image')

    if not name or not image:
        return jsonify({"error": "Name and image are required"}), 400

    # forward the multipart data to backend
    files = {'image': (image.filename, image.stream, image.mimetype)}
    data = {'name': name}
    # if successful, backend returns {"status": "saved", ...}
    # assign points randomly for demo purposes
    #

    try:
        resp = requests.post(BACKEND_URL, data=data, files=files, timeout=10)
        return jsonify(resp.json()), resp.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Backend unreachable", "detail": str(e)}), 502

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
