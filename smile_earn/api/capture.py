# from flask import Flask, request, jsonify
# import cv2, os, time, json
# from datetime import datetime

# app = Flask(__name__)

# # Adjust to your working device (Brio often exposes /dev/video2 or /dev/video3)
# CAPTURE_DEVICE = "/dev/video0"

# BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# CAPTURE_DIR = os.path.join(BASE_DIR, 'data', 'captures')
# os.makedirs(CAPTURE_DIR, exist_ok=True)

# def capture_frame(device):
#     cap = cv2.VideoCapture(device, cv2.CAP_V4L2)  # force V4L2 on Linux
#     # reasonable defaults for Brio 100
#     cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
#     cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
#     cap.set(cv2.CAP_PROP_FPS, 30)

#     time.sleep(2.5)  # warm-up

#     ret, frame = cap.read()
#     # retry a few times in case first frame is empty
#     for _ in range(3):
#         if ret and frame is not None:
#             break
#         time.sleep(0.5)
#         ret, frame = cap.read()

#     cap.release()
#     if not ret or frame is None:
#         raise RuntimeError("Failed to grab frame from camera")
#     return frame

# @app.route('/capture', methods=['POST'])
# def capture():
#     # optional: receive cart metadata (not required for capture)
#     cart_raw = request.form.get("cart")
#     cart = []
#     if cart_raw:
#         try:
#             cart = json.loads(cart_raw)
#         except Exception:
#             pass

#     try:
#         frame = capture_frame(CAPTURE_DEVICE)
#         ts = datetime.now().strftime("%Y%m%d_%H%M%S")
#         img_path = os.path.join(CAPTURE_DIR, f"checkout_{ts}.jpg")
#         cv2.imwrite(img_path, frame)
#         rel_path = os.path.relpath(img_path, start=BASE_DIR)
#         return jsonify({
#             "status": "captured",
#             "image_path": rel_path,
#             "cart_echo": cart
#         }), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# if __name__ == '__main__':
#     # run this separately from the shop app
#     app.run(host='0.0.0.0', port=5004, debug=True)
