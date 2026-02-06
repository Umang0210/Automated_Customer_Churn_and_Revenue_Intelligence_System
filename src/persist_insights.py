import json
import joblib
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine


# -----------------------------
# CONFIG
# -----------------------------
DB_URI = "mysql+pymysql://username:password@localhost:3306/churn_intelligence"

DATA_PATH = "data/processed/customer_features.csv"
MODEL_PATH = "models/churn_model.pkl"
FEATURES_PATH = "models/feature_list.json"
METADATA_PATH = "models/model_metadata.json"


# -----------------------------
# DB CONNECTION
# -----------------------------
engine = create_engine(DB_URI)


# -----------------------------
# LOAD DATA & ARTIFACTS
# -----------------------------
df = pd.read_csv(DATA_PATH)

df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)

model = joblib.load(MODEL_PATH)

with open(FEATURES_PATH) as f:
    feature_list = json.load(f)

with open(METADATA_PATH) as f:
    metadata = json.load(f)

model_version = metadata["model_version"]
timestamp = datetime.utcnow()

