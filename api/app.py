from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd
import json

app = FastAPI(title="Churn Prediction API")

# ======================
# Configuration
# ======================
HIGH_RISK_THRESHOLD = 0.7
MEDIUM_RISK_THRESHOLD = 0.4

# ======================
# Load Assets
# ======================
model = joblib.load("models/churn_model.pkl")

try:
    scaler = joblib.load("models/scaler.pkl")
except FileNotFoundError:
    scaler = None

try:
    with open("models/feature_list.json", "r") as f:
        feature_list = json.load(f)
except FileNotFoundError:
    feature_list = []

# ======================
# Schemas
# ======================
class ChurnRequest(BaseModel):
    customer_id: int
    monthly_charges: float
    usage_frequency: int
    complaints_count: int
    payment_delays: int

    # optional categorical fields (future-safe)
    gender: str | None = "missing"
    seniorcitizen: str | None = "missing"
    contract: str | None = "missing"


class ChurnResponse(BaseModel):
    customer_id: int
    churn_probability: float
    risk_level: str
    expected_revenue_loss: float
    priority_score: float


# ======================
# Health
# ======================
@app.get("/health")
def health():
    return {"status": "ok"}


# ======================
# Prediction
# ======================
@app.post("/predict", response_model=ChurnResponse)
def predict(request: ChurnRequest):

    # 1. Create DataFrame
    df = pd.DataFrame([request.dict()])

    # 2. Normalize column names
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # 3. One-hot encoding
    CATEGORICAL_COLS = ["gender", "seniorcitizen", "contract"]

    for col in CATEGORICAL_COLS:
        if col not in df.columns:
            df[col] = "missing"

    df_encoded = pd.get_dummies(df, columns=CATEGORICAL_COLS, drop_first=True)

    # 4. Align features with training
    if feature_list:
        df_final = df_encoded.reindex(columns=feature_list, fill_value=0)
    else:
        df_final = df_encoded

    # 5. Scale
    if scaler:
        X = scaler.transform(df_final)
    else:
        X = df_final

    # 6. Predict
    prob = float(model.predict_proba(X)[0][1])

    # 7. Risk bucket
    if prob >= HIGH_RISK_THRESHOLD:
        risk = "HIGH"
    elif prob >= MEDIUM_RISK_THRESHOLD:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    # 8. Business logic
    expected_loss = request.monthly_charges * 12
    priority_score = prob * expected_loss

    return ChurnResponse(
        customer_id=request.customer_id,
        churn_probability=round(prob, 4),
        risk_level=risk,
        expected_revenue_loss=round(expected_loss, 2),
        priority_score=round(priority_score, 2)
    )


# ======================
# Root
# ======================
@app.get("/")
def root():
    return {
        "service": "churn-ml-api",
        "status": "running",
        "health": "/health",
        "predict": "/predict"
    }