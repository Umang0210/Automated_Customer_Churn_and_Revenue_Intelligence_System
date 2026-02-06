from fastapi import FastAPI
import joblib
import pandas as pd
import json

app = FastAPI(title="Churn Prediction API")

# Load Assets
model = joblib.load("models/churn_model.pkl")

try:
    scaler = joblib.load("models/scaler.pkl")
except FileNotFoundError:
    scaler = None

try:
    with open("models/feature_list.json", "r") as f:
        feature_list = json.load(f)
except FileNotFoundError:
    feature_list = []  # Fallback or error

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict")
def predict(data: dict):
    # 1. Create DataFrame
    df = pd.DataFrame([data])
    
    # 2. Preprocessing (match train.py)
    # Normalize columns
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    
    # One-hot encode
    CATEGORICAL_COLS = ["gender", "seniorcitizen", "contract"]
    # Ensure raw df has these cols (even if None) to avoid get_dummies error if missing entirely
    for col in CATEGORICAL_COLS:
        if col not in df.columns:
            df[col] = "missing"
            
    df_encoded = pd.get_dummies(df, columns=CATEGORICAL_COLS, drop_first=True)
    
    # 3. Align Columns with Training Schema
    # This ensures exact same columns in exact same order
    if feature_list:
        df_final = df_encoded.reindex(columns=feature_list, fill_value=0)
    else:
        df_final = df_encoded

    # 4. Scale if scaler exists
    if scaler:
        X = scaler.transform(df_final)
    else:
        X = df_final

    # 5. Predict
    prob = model.predict_proba(X)[0][1]

    return {
        "churn_probability": round(float(prob), 4),
        "risk_level": "HIGH" if prob > 0.7 else "MEDIUM" if prob > 0.4 else "LOW"
    }


@app.get("/")
def root():
    return {
        "service": "churn-ml-api",
        "status": "running",
        "health": "/health",
        "predict": "/predict"
    }
