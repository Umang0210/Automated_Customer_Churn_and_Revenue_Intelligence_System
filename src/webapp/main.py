from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import pandas as pd
import os
import json

app = FastAPI(title="Churn Insights Dashboard")

# CONFIG
DB_URI = "mysql+pymysql://churn_user:StrongPassword123@localhost:3306/churn_intelligence"
engine = create_engine(DB_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# MOUNT STATIC FILES
# This serves the frontend
app.mount("/static", StaticFiles(directory="src/webapp/static"), name="static")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

@app.get("/")
def read_root():
    return {"message": "Welcome to Churn Insights API. Go to /static/index.html for the dashboard."}
