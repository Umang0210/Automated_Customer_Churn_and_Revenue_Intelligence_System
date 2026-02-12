import json
import joblib
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, precision_score, recall_score

# ==============================
# CONFIG
# ==============================
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "processed" / "customer_features.csv"
MODEL_DIR = BASE_DIR / "models"

TARGET_COL = "churn"
RANDOM_STATE = 42


# ==============================
# HELPER: EVALUATE MODEL
# ==============================
def evaluate_model(model, X_test, y_test, threshold=0.5):
    y_prob = model.predict_proba(X_test)[:, 1]
    y_pred = (y_prob >= threshold).astype(int)

    return {
        "roc_auc": round(roc_auc_score(y_test, y_prob), 4),
        "precision": round(precision_score(y_test, y_pred), 4),
        "recall": round(recall_score(y_test, y_pred), 4),
    }


# ==============================
# MAIN TRAINING PIPELINE
# ==============================
def main():

    print("Loading data...")
    df = pd.read_csv(DATA_PATH)

    # Normalize schema
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # Map target if string
    if df[TARGET_COL].dtype == object:
        df[TARGET_COL] = df[TARGET_COL].map({'yes': 1, 'no': 0})

    # Drop ID safely
    df = df.drop(columns=["customerid"], errors="ignore")

    # Feature groups
    NUMERIC_COLS = ["tenure", "monthlycharges", "totalcharges"]
    CATEGORICAL_COLS = ["gender", "seniorcitizen", "contract"]

    X = df[NUMERIC_COLS + CATEGORICAL_COLS]
    y = df[TARGET_COL]

    # Encode categoricals
    X = pd.get_dummies(X, columns=CATEGORICAL_COLS, drop_first=True)
    feature_list = list(X.columns)

    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=y
    )

    # ==============================
    # LOGISTIC REGRESSION
    # ==============================
    scaler = StandardScaler()

    X_train_scaled = X_train.copy()
    X_test_scaled = X_test.copy()

    X_train_scaled[NUMERIC_COLS] = scaler.fit_transform(X_train[NUMERIC_COLS])
    X_test_scaled[NUMERIC_COLS] = scaler.transform(X_test[NUMERIC_COLS])

    log_reg = LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        random_state=RANDOM_STATE
    )

    log_reg.fit(X_train_scaled, y_train)
    log_reg_metrics = evaluate_model(log_reg, X_test_scaled, y_test)

    # ==============================
    # RANDOM FOREST
    # ==============================
    rf = RandomForestClassifier(
        n_estimators=250,
        max_depth=10,
        class_weight="balanced",
        random_state=RANDOM_STATE,
        n_jobs=-1
    )

    rf.fit(X_train, y_train)
    rf_metrics = evaluate_model(rf, X_test, y_test)

    # ==============================
    # MODEL SELECTION
    # ==============================
    if rf_metrics["roc_auc"] >= log_reg_metrics["roc_auc"]:
        selected_model = "random_forest"
        final_model = rf
        final_scaler = None
        final_metrics = rf_metrics
    else:
        selected_model = "logistic_regression"
        final_model = log_reg
        final_scaler = scaler
        final_metrics = log_reg_metrics

    # ==============================
    # SAVE ARTIFACTS
    # ==============================
    MODEL_DIR.mkdir(exist_ok=True)

    joblib.dump(final_model, MODEL_DIR / "churn_model.pkl")

    if final_scaler:
        joblib.dump(final_scaler, MODEL_DIR / "scaler.pkl")

    with open(MODEL_DIR / "feature_list.json", "w") as f:
        json.dump(feature_list, f, indent=4)

    metadata = {
        "model_version": "v1.1.0",
        "training_date": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "selected_model": selected_model,
        "metrics": {
            "logistic_regression": log_reg_metrics,
            "random_forest": rf_metrics
        },
        "final_model_metrics": final_metrics,
        "num_features": len(feature_list)
    }

    with open(MODEL_DIR / "model_metadata.json", "w") as f:
        json.dump(metadata, f, indent=4)

    print("\n✅ Training completed successfully")
    print(f"✅ Selected model: {selected_model}")
    print("📊 Final metrics:", final_metrics)


if __name__ == "__main__":
    main()
