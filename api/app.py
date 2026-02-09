from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd
import json
import mysql.connector

# ===============================
# App Init
# ===============================
app = FastAPI(title="Churn Intelligence API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===============================
# Load ML Assets
# ===============================
model = joblib.load("models/churn_model.pkl")

try:
    scaler = joblib.load("models/scaler.pkl")
except:
    scaler = None

try:
    with open("models/feature_list.json", "r") as f:
        feature_list = json.load(f)
except:
    feature_list = []

# ===============================
# Database Connection
# ===============================
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",          # later: mysql container / RDS
        user="churn_user",
        password="StrongPassword123",
        database="churn_intelligence"
    )

def insert_prediction(
    customer_id,
    churn_probability,
    risk_bucket,
    revenue,
    expected_revenue_loss,
    priority_score,
    model_version
):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO customers_predictions (
            customer_id,
            churn_probability,
            risk_bucket,
            revenue,
            expected_revenue_loss,
            priority_score,
            model_version
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    cursor.execute(query, (
        customer_id,
        churn_probability,
        risk_bucket,
        revenue,
        expected_revenue_loss,
        priority_score,
        model_version
    ))

    conn.commit()
    cursor.close()
    conn.close()

# ===============================
# Request Schema
# ===============================
class ChurnRequest(BaseModel):
    customer_id: str
    revenue: float

    monthly_charges: float
    usage_frequency: int
    complaints_count: int
    payment_delays: int

    gender: str | None = "missing"
    seniorcitizen: str | None = "missing"
    contract: str | None = "missing"

# ===============================
# Health
# ===============================
@app.get("/health")
def health():
    return {"status": "ok"}

# ===============================
# Predict + Persist
# ===============================
@app.post("/predict")
def predict(request: ChurnRequest):

    # ---- Build DataFrame ----
    df = pd.DataFrame([request.dict()])
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    categorical_cols = ["gender", "seniorcitizen", "contract"]
    for col in categorical_cols:
        if col not in df.columns:
            df[col] = "missing"

    df_encoded = pd.get_dummies(df, columns=categorical_cols, drop_first=True)

    if feature_list:
        df_final = df_encoded.reindex(columns=feature_list, fill_value=0)
    else:
        df_final = df_encoded

    X = scaler.transform(df_final) if scaler else df_final

    # ---- ML Prediction ----
    prob = float(model.predict_proba(X)[0][1])

    if prob >= 0.7:
        risk = "HIGH"
    elif prob >= 0.4:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    expected_loss = round(prob * request.revenue, 2)
    priority_score = round(prob * expected_loss, 2)
    model_version = "v1.0"

    # ---- Insert into MySQL ----
    insert_prediction(
        customer_id=request.customer_id,
        churn_probability=round(prob, 4),
        risk_bucket=risk,
        revenue=request.revenue,
        expected_revenue_loss=expected_loss,
        priority_score=priority_score,
        model_version=model_version
    )

    # ---- API Response ----
    return {
        "customer_id": request.customer_id,
        "churn_probability": round(prob, 4),
        "risk_bucket": risk,
        "expected_revenue_loss": expected_loss,
        "priority_score": priority_score
    }

# ===============================
# GET APIs FOR FRONTEND
# ===============================

@app.get("/api/customers")
def get_customers():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            customer_id,
            churn_probability,
            risk_bucket,
            revenue,
            expected_revenue_loss,
            priority_score,
            model_version,
            prediction_timestamp
        FROM customers_predictions
        ORDER BY priority_score DESC
        LIMIT 100
    """)

    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data


@app.get("/api/kpis")
def get_kpis():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            COUNT(*) AS total_customers,
            SUM(CASE WHEN risk_bucket = 'HIGH' THEN 1 ELSE 0 END) AS high_risk_customers,
            ROUND(SUM(CASE WHEN risk_bucket = 'HIGH' THEN expected_revenue_loss ELSE 0 END), 2)
                AS revenue_at_risk
        FROM customers_predictions
    """)

    data = cursor.fetchone()
    cursor.close()
    conn.close()
    return data


@app.get("/api/risk_distribution")
def risk_distribution():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            risk_bucket,
            COUNT(*) AS count
        FROM customers_predictions
        GROUP BY risk_bucket
    """)

    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data


@app.get("/api/segments")
def segment_insights():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            segment_type,
            segment_value,
            churn_rate,
            customer_count,
            generated_at
        FROM segment_insights
        ORDER BY churn_rate DESC
    """)

    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

# ===============================
# Root
# ===============================
@app.get("/")
def root():
    return {
        "service": "churn-intelligence-api",
        "status": "running",
        "endpoints": [
            "/predict",
            "/api/customers",
            "/api/kpis",
            "/api/risk_distribution",
            "/api/segments"
        ]
    }

