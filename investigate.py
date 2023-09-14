from sklearn import svm
import cv2
import numpy as np

def extract_features(image_path):
    img = cv2.imread(image_path, 0)
    if img is None:
        print(f"Error: Unable to load image {image_path}")
        return None
    return np.array([np.mean(img), np.var(img)])

def train_classifier():
    X = []
    y = []

    for img_path, label in [('signature1.png', '001'), ('signature2.png', '001')]:
        features = extract_features(img_path)
        if features is not None:
            X.append(features)
            y.append(label)
        else:
            print(f"Error: One or more images could not be processed.")
            return None

    if len(X) == 0 or len(y) == 0:
        print("Error: No valid data for training.")
        return None

    clf = svm.SVC()
    clf.fit(X, y)
    return clf