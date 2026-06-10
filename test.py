"""
test.py
Loads savedmodel.pth, evaluates it on the test split, and prints accuracy.
"""

import joblib
from sklearn.datasets import fetch_olivetti_faces
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# ── 1. Re-create the same test split ──────────────────────────────────────────
print("Loading Olivetti faces dataset...")
data = fetch_olivetti_faces(shuffle=True, random_state=42)
X, y = data.data, data.target

_, X_test, _, y_test = train_test_split(
    X, y, test_size=0.30, random_state=42, stratify=y
)
print(f"Test samples: {len(X_test)}")

# ── 2. Load model ──────────────────────────────────────────────────────────────
print("Loading savedmodel.pth...")
model = joblib.load("savedmodel.pth")
print("Model loaded successfully.")

# ── 3. Evaluate ────────────────────────────────────────────────────────────────
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print("\n" + "=" * 45)
print(f"  Test Accuracy : {accuracy * 100:.2f}%")
print("=" * 45)
print("\nDetailed Classification Report:")
print(classification_report(y_test, y_pred))
