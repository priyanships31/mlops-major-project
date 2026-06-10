"""
app.py
Flask web application that serves a face-recognition interface.
Users upload a 64×64 grayscale image; the app returns the predicted subject ID.
"""

import io
import joblib
import numpy as np
from flask import Flask, render_template, request, jsonify
from PIL import Image

app = Flask(__name__)

# ── Load model once at startup ─────────────────────────────────────────────────
MODEL_PATH = "savedmodel.pth"
model = joblib.load(MODEL_PATH)
print(f"[INFO] Model loaded from {MODEL_PATH}")


def preprocess_image(file_storage) -> np.ndarray:
    """
    Convert an uploaded image to the 4096-feature vector expected by the model.
    Steps:
        1. Open image with Pillow
        2. Convert to greyscale
        3. Resize to 64×64
        4. Normalise pixel values to [0, 1]
        5. Flatten to (1, 4096)
    """
    img = Image.open(io.BytesIO(file_storage.read())).convert("L")
    img = img.resize((64, 64))
    arr = np.array(img, dtype=np.float32) / 255.0
    return arr.flatten().reshape(1, -1)


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "No image file provided."}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "Empty filename."}), 400

    try:
        features = preprocess_image(file)
        predicted_class = int(model.predict(features)[0])
        probabilities = None

        # DecisionTreeClassifier supports predict_proba
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(features)[0]
            confidence = float(proba[predicted_class]) * 100
        else:
            confidence = None

        return jsonify({
            "predicted_class": predicted_class,
            "confidence": f"{confidence:.2f}%" if confidence is not None else "N/A",
            "message": f"Predicted Subject ID: {predicted_class}"
        })

    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/health")
def health():
    return jsonify({"status": "healthy", "model": MODEL_PATH}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
