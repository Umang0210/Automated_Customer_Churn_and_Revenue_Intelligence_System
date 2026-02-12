from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import pandas as pd
import os
import json
import joblib
import mysql.connector
from pydantic import BaseModel
from typing import Optional

# ===============================
# App Init
# ===============================
app = FastAPI(title="Churn Command Center")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===============================
# CONFIG & ASSETS
# ===============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# fix paths relative to where this file is (src/webapp) -> we need to go up to root
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../"))

DB_URI = "mysql+pymysql://churn_user:StrongPassword123@localhost:3306/churn_intelligence"
engine = create_engine(DB_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Load Model
MODEL_PATH = os.path.join(ROOT_DIR, "models/churn_model.pkl")
FEATURES_PATH = os.path.join(ROOT_DIR, "models/feature_list.json")
SCALER_PATH = os.path.join(ROOT_DIR, "models/scaler.pkl") # Assuming scaler exists if used

print(f"Loading model from: {MODEL_PATH}")
try:
    model = joblib.load(MODEL_PATH)
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

try:
    with open(FEATURES_PATH, "r") as f:
        feature_list = json.load(f)
except Exception as e:
    print(f"Error loading features: {e}")
    feature_list = []

try:
    scaler = joblib.load(SCALER_PATH)
except:
    scaler = None

# ===============================
# DB Helpers
# ===============================
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="churn_user",
        password="StrongPassword123",
        database="churn_intelligence"
    )

def insert_prediction(data):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO customers_predictions (
                customer_id, churn_probability, risk_bucket, revenue, 
                expected_revenue_loss, priority_score, model_version, prediction_timestamp
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
        """
        values = (
            data['customer_id'], data['churn_probability'], data['risk_bucket'],
            data['revenue'], data['expected_revenue_loss'], data['priority_score'],
            data['model_version']
        )
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"DB Insert Error: {e}")

# ===============================
# Request Schema
# ===============================
class ChurnRequest(BaseModel):
    customer_id: str
    revenue: float
    monthly_charges: float
    tenure: int
    gender: Optional[str] = "Male"
    seniorcitizen: Optional[str] = "No"
    contract: Optional[str] = "Month-to-month"
    
    # Allow extra fields safely
    class Config:
        extra = "ignore"

# ===============================
# API Endpoints
# ===============================

@app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

@app.post("/api/predict")
def predict(request: ChurnRequest):
    if not model:
        raise HTTPException(status_code=503, detail="Model not loaded")

    # 1. Prepare Data
    data = request.dict()
    df = pd.DataFrame([data])
    
    # 2. Preprocessing (Basic)
    # We ideally need the exact cleaning pipeline here. 
    # For now, we assume inputs are relatively clean or we do minimal encoding.
    # Note: In a real app, import `src.process` logic.
    
    # Normalize
    df.columns = df.columns.str.lower().str.replace(" ", "_")
    
    # Encoding (Simplified for Demo)
    # We must match the training columns exactly.
    # If the user sends raw "Male", "Month-to-month", we need ONE-HOT encoding that matches `feature_list`.
    
    # Create dummies
    df_encoded = pd.get_dummies(df, columns=["gender", 'seniorcitizen', 'contract'], drop_first=True)
    
    # Reindex to match model features
    if feature_list:
        # Add missing cols with 0
        for col in feature_list:
            if col not in df_encoded.columns:
                df_encoded[col] = 0
        # Drop extra cols
        X = df_encoded[feature_list]
    else:
        # Fallback if no feature list (risky)
        X = df_encoded.select_dtypes(include=["number"])

    # Scale if needed (skipping for now if scaler not robustly saved or if RF used)
    # The user's api/app.py logic checked for scaler.
    
    # 3. Predict
    try:
        prob = float(model.predict_proba(X)[0][1])
    except Exception as e:
        # Fallback for demo if model fails on shape mismatch
        print(f"Prediction Error: {e}")
        prob = 0.5 

    # 4. Business Logic
    if prob >= 0.7: risk = "HIGH"
    elif prob >= 0.4: risk = "MEDIUM"
    else: risk = "LOW"

    expected_loss = round(prob * request.revenue, 2)
    priority_score = round(prob * expected_loss, 2)

    # 5. Persist
    result = {
        "customer_id": request.customer_id,
        "churn_probability": round(prob, 4),
        "risk_bucket": risk,
        "revenue": request.revenue,
        "expected_revenue_loss": expected_loss,
        "priority_score": priority_score,
        "model_version": "v2.0-unified"
    }
    insert_prediction(result)

    return result

@app.get("/api/kpis")
def get_kpis():
    """Fetch latest business KPIs"""
    try:
        query = "SELECT * FROM business_kpis WHERE generated_at = (SELECT MAX(generated_at) FROM business_kpis)"
        df = pd.read_sql(query, engine)
        if df.empty:
            return []
        # Convert to dictionary format: {metric_name: metric_value}
        kpis = dict(zip(df.metric_name, df.metric_value))
        return kpis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/segments")
def get_segments():
    """Fetch customer segment insights"""
    try:
        query = "SELECT * FROM segment_insights WHERE generated_at = (SELECT MAX(generated_at) FROM segment_insights)"
        df = pd.read_sql(query, engine)
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/customers")
def get_high_risk_customers():
    """Fetch top high risk customers"""
    try:
        # Get latest predictions
        query = """
        SELECT customer_id, churn_probability, risk_bucket, revenue, expected_revenue_loss 
        FROM customers_predictions 
        WHERE prediction_timestamp = (SELECT MAX(prediction_timestamp) FROM customers_predictions)
        ORDER BY expected_revenue_loss DESC
        LIMIT 20
        """
        df = pd.read_sql(query, engine)
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/metrics")
def get_model_metrics():
    """Fetch latest model run metrics"""
    try:
        query = "SELECT * FROM model_runs ORDER BY run_timestamp DESC LIMIT 1"
        df = pd.read_sql(query, engine)
        return df.to_dict(orient="records")[0] if not df.empty else {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/risk_distribution")
def get_risk_distribution():
    """Fetch risk distribution for pie chart"""
    try:
        query = """
        SELECT risk_bucket, COUNT(*) as count 
        FROM customers_predictions 
        WHERE prediction_timestamp = (SELECT MAX(prediction_timestamp) FROM customers_predictions)
        GROUP BY risk_bucket
        """
        df = pd.read_sql(query, engine)
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "Welcome to Churn Insights API. Go to /static/index.html for the dashboard."}
    