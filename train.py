"""
train.py
Loads the Olivetti faces dataset, splits it 70/30, trains a
DecisionTreeClassifier, and saves the model as savedmodel.pth using joblib.
"""

import joblib
from sklearn.datasets import fetch_olivetti_faces
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

# ── 1. Load dataset ────────────────────────────────────────────────────────────
print("Loading Olivetti faces dataset...")
data = fetch_olivetti_faces(shuffle=True, random_state=42)
X, y = data.data, data.target          # X: (400, 4096), y: (400,)
print(f"Dataset shape  → X: {X.shape}, y: {y.shape}")
print(f"Number of classes: {len(set(y))}")

# ── 2. Train / test split (70 / 30) ───────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.30, random_state=42, stratify=y
)
print(f"Train samples  : {len(X_train)}")
print(f"Test  samples  : {len(X_test)}")

# ── 3. Train model ─────────────────────────────────────────────────────────────
print("\nTraining DecisionTreeClassifier...")
model = DecisionTreeClassifier(random_state=42)
model.fit(X_train, y_train)
print("Training complete.")

# ── 4. Save model ──────────────────────────────────────────────────────────────
joblib.dump(model, "savedmodel.pth")
print("Model saved as savedmodel.pth")
