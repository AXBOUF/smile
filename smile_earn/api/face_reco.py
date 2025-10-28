import cv2
import face_recognition
import numpy as np
import pickle
import json
import sys

# Load pre-trained encodings
print("[INFO] Loading known faces...")
with open("encodings.pickle", "rb") as f:
    data = pickle.loads(f.read())
known_face_encodings = data["encodings"]
known_face_names = data["names"]



def capture_frame():
    cap = cv2.VideoCapture("/dev/video0")
    cap.set(3, 1280)
    cap.set(4, 720)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open camera {"/dev/video0"}")

    ret, frame = cap.read()
    cap.release()
    if not ret:
        raise RuntimeError("Failed to capture frame")
    return frame

def recognize_face(frame):
    # Convert image to RGB (OpenCV loads BGR)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Detect faces and compute encodings
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations, model="large")

    # Default result
    result = {"person": "Unknown"}

    if len(face_encodings) > 0:
        face_encoding = face_encodings[0]
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_names[best_match_index]
            result["person"] = name
    return result

def main():
    print("[READY] Press ENTER to capture, 'q' to quit (or Ctrl+C).")
    while True:
        try:
            key = input().strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n[EXIT] Interrupted. Shutting down gracefully.")
            sys.exit(0)

        # If just Enter pressed (blank input) → capture frame
        if key == "":
            frame = capture_frame()
            result = recognize_face(frame)
            print(json.dumps(result))

        elif key == "q":
            print("[EXIT] Quitting face recognition.")
            break

        else:
            print("[INFO] Unknown command. Press ENTER to capture or 'q' to quit.")


if __name__ == "__main__":
    main()
