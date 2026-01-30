import os
import json
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
import joblib

DATA_PATH = "data/processed/customer_features.csv"
MODEL_DIR = "models"
TARGET_COL = "churn"


def train_model():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError("Feature dataset not found. Run features.py first.")

    df = pd.read_csv(DATA_PATH)

    if TARGET_COL not in df.columns:
        raise ValueError("Target column not found.")

    X = df.drop(columns=[TARGET_COL])
    y = df[TARGET_COL]

    # Save feature names (important for inference)
    feature_names = X.columns.tolist()

    # One-hot encode categoricals
    X = pd.get_dummies(X, drop_first=True)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train_scaled, y_train)

    y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
    auc = roc_auc_score(y_test, y_pred_proba)

    os.makedirs(MODEL_DIR, exist_ok=True)

    joblib.dump(model, f"{MODEL_DIR}/churn_model.pkl")
    joblib.dump(scaler, f"{MODEL_DIR}/scaler.pkl")

    with open(f"{MODEL_DIR}/feature_list.json", "w") as f:
        json.dump(feature_names, f)

    print(f"Model trained successfully")
    print(f"ROC-AUC: {auc:.4f}")


if __name__ == "__main__":
    train_model()
