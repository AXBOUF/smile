import os
from imutils import paths
import face_recognition
import pickle
import cv2

def train_all_faces(dataset_dir="data/dataset", output_path="encodings.pickle"):
    print("[INFO] start processing faces...")
    imagePaths = list(paths.list_images(dataset_dir))
    knownEncodings, knownNames = [], []

    for (i, imagePath) in enumerate(imagePaths):
        name = imagePath.split(os.path.sep)[-2]
        image = cv2.imread(imagePath)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        boxes = face_recognition.face_locations(rgb, model="hog")
        encodings = face_recognition.face_encodings(rgb, boxes)
        for encoding in encodings:
            knownEncodings.append(encoding)
            knownNames.append(name)

    data = {"encodings": knownEncodings, "names": knownNames}
    with open(output_path, "wb") as f:
        pickle.dump(data, f)

    print("[INFO] Training complete.")
    return {"status":"trained","faces":len(knownNames),"pickle":output_path}
