# 📊 Customer Churn & Revenue Optimization Intelligence System

**End-to-End Data Science + Machine Learning + DevOps**

> **Status:** ✅ Active Development | 🚀 Core Pipeline Complete

A production-ready decision intelligence system that predicts customer churn, quantifies revenue risk, and empowers business stakeholders with actionable insights. Covers the complete ML lifecycle — raw data to deployed API with real-time dashboard.

---

## 🔍 Problem Statement

Customer churn directly impacts revenue, but most organizations detect it **after** the loss occurs. This system answers three critical business questions:

1. **Who is likely to churn next?** ← Predictive ML
2. **How much revenue is at risk?** ← Business Intelligence
3. **Which customers do we save first?** ← Prescriptive Decision Intelligence

---

## 🎯 Solution Architecture

### Four Integrated Subsystems

| Subsystem | Components | Output |
|-----------|------------|--------|
| **Data & ML Pipeline** | Ingestion → Cleaning → Feature Engineering → EDA → Training → Evaluation | Trained model, evaluation report, EDA plots |
| **Inference Services** | Real-time FastAPI `/predict` + Batch `persist_insights.py` | Churn probability, risk bucket, priority score |
| **Database Layer** | MySQL `customer_churn_analytics` table | Persisted predictions for dashboard |
| **Web Dashboard** | 5-page HTML/JS frontend + FastAPI backend | Live KPI views, customer risk tables |

### Data Flow

```
Raw CSV
  └── ingestion.py       → data/raw snapshot
  └── cleaning.py        → data/processed/clean_customers.csv
  └── features.py        → data/processed/customer_features.csv
  └── eda.py             → reports/figures/ (8 plots) + business_insights.csv
  └── train.py           → models/ (pkl, json artifacts)
  └── evaluate.py        → reports/evaluation_report.json (4 plots)
  └── persist_insights.py → MySQL + reports/batch_predictions.csv
  └── business_insights.py → reports/segment_summary.csv + top_priority_customers.csv
                                        ↓
                               FastAPI  api/app.py
                                        ↓
                            Web Dashboard (src/webapp/)
```

---

## 🤖 ML Models

Three models are trained and auto-compared. The best by ROC-AUC is selected automatically.

| Model | Type | Notes |
|-------|------|-------|
| **Logistic Regression** | Linear baseline | StandardScaler applied, class-balanced |
| **Random Forest** | Ensemble, non-linear | 200 trees, class-balanced, no scaling needed |
| **XGBoost** | Gradient boosting | 300 estimators, scale_pos_weight auto-tuned for class imbalance |

**Why these three?** Interpretable, industry-standard, recruiter-safe. The PDF spec explicitly lists them.

**Model outputs per customer:**
- Churn probability (0–100%)
- Risk bucket: `Low` (<40%) / `Medium` (40–70%) / `High` (>70%)
- Expected revenue loss = `churn_probability × revenue`
- Priority score = `churn_probability × expected_revenue_loss`

---

## 📈 Current Model Performance

| Metric | Value |
|--------|-------|
| ROC-AUC | 0.85+ |
| Precision (@ 0.5) | 0.78+ |
| Recall (@ 0.5) | 0.72+ |
| CI/CD Gate | Minimum ROC-AUC = 0.70 |

Threshold analysis runs at 0.4 / 0.5 / 0.6 / 0.7 — see `reports/evaluation_report.json`.

---

## 📁 Project Structure

```
Customer_Churn_and_Revenue_Intelligence_System/
│
├── .github/workflows/
│   └── data_pipeline.yml        # CI/CD — automated testing + performance gate
│
├── api/
│   ├── app.py                   # FastAPI inference API (v3.0.0)
│   ├── customers.py             # Customer endpoints
│   ├── kpis.py                  # KPI endpoints
│   ├── risk_distribution.py     # Risk analytics
│   └── segments.py              # Segmentation endpoints
│
├── data/
│   ├── raw/                     # Original CSV (Sample_dataset.csv tracked)
│   └── processed/               # Cleaned + feature-engineered CSVs (gitignored)
│
├── models/
│   ├── churn_model.pkl          # Best trained model (gitignored — regenerate locally)
│   ├── scaler.pkl               # Feature scaler if applicable (gitignored)
│   ├── feature_list.json        # Feature schema (tracked)
│   └── model_metadata.json      # Training metrics + model info (gitignored)
│
├── src/
│   ├── webapp/                  # Web Dashboard
│   │   ├── static/
│   │   │   ├── index.html       # Executive KPI dashboard
│   │   │   ├── customers.html   # Customer risk table
│   │   │   ├── analytics.html   # Segment analysis
│   │   │   ├── predictions.html # Model prediction explorer
│   │   │   ├── settings.html    # Threshold + config
│   │   │   ├── script.js        # Live API integration
│   │   │   └── style.css
│   │   └── main.py              # Dashboard FastAPI backend
│   │
│   ├── ingestion.py             # Step 1 — Raw data load + snapshot
│   ├── cleaning.py              # Step 2 — Data cleaning → clean_customers.csv
│   ├── features.py              # Step 3 — Feature engineering → customer_features.csv
│   ├── eda.py                   # Step 4 — EDA plots + business_insights.csv
│   ├── train.py                 # Step 5 — Train LR + RF + XGBoost, auto-select best
│   ├── evaluate.py              # Step 6 — Evaluate model, threshold analysis, CI/CD gate
│   ├── persist_insights.py      # Step 7 — Batch predictions → MySQL + CSV
│   └── business_insights.py     # Step 8 — KPI aggregation + priority customer ranking
│
├── reports/
│   ├── figures/                 # 12 auto-generated plots (gitignored)
│   ├── business_insights.csv    # 20+ KPI metrics
│   ├── segment_summary.csv      # Risk bucket breakdown
│   ├── top_priority_customers.csv # Top 20 customers to target
│   ├── batch_predictions.csv    # Full dataset predictions
│   ├── evaluation_report.json   # Model metrics + gate result
│   └── README.md                # Reports documentation
│
├── Power BI/                    # Power BI dashboard (.pbix)
│
├── .dockerignore
├── .gitignore
├── ARCHITECTURE.md
├── Dockerfile
├── Dockerfile.webapp
├── Jenkinsfile                  # Jenkins CI/CD pipeline
├── amplify.yml
├── docker-compose.yml
├── main.sql                     # MySQL schema
├── requirements.txt
│
├── aws/                         # AWS deployment configs
│   ├── ecr-setup.sh            # One-time ECR repo creation
│   ├── ecs-task-definition.json # Fargate task definition
│   └── ecs-service.sh          # One-time ECS cluster + service setup
│
└── README.md                    # This file
```

---

## 🚀 How to Run Locally

### Prerequisites
- Python 3.11+
- MySQL Server (for dashboard/API; optional for EDA + training)
- Git

### 1. Clone & Install

```bash
git clone https://github.com/Umang0210/Customer_Churn_and_Revenue_Intelligence_System.git
cd Customer_Churn_and_Revenue_Intelligence_System
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Database (optional)

Create a `.env` file in the project root:

```env
DB_HOST=localhost
DB_USER=churn_user
DB_PASSWORD=StrongPassword123
DB_NAME=churn_intelligence
MODEL_VERSION=v2.0.0
```

```sql
CREATE DATABASE churn_intelligence;
CREATE USER 'churn_user'@'localhost' IDENTIFIED BY 'StrongPassword123';
GRANT ALL PRIVILEGES ON churn_intelligence.* TO 'churn_user'@'localhost';
FLUSH PRIVILEGES;
```

### 3. Run the Full Pipeline

```bash
python src/ingestion.py           # Load raw data
python src/cleaning.py            # Clean data
python src/features.py            # Engineer features
python src/eda.py                 # EDA plots + business insights
python src/train.py               # Train LR + RF + XGBoost, auto-select best
python src/evaluate.py            # Evaluate + threshold analysis (exits 1 if AUC < 0.70)
python src/persist_insights.py    # Batch predictions → MySQL + CSV
python src/business_insights.py   # KPI aggregation + priority ranking
```

### 4. Start the Inference API

```bash
python -m uvicorn api.app:app --port 5000 --reload
```

- Swagger docs: http://127.0.0.1:5000/docs

### 5. Start the Web Dashboard

```bash
python -m uvicorn src.webapp.main:app --port 8000 --reload
```

Dashboard pages:
- **Executive KPIs**: http://127.0.0.1:8000/static/index.html
- **Customers**: http://127.0.0.1:8000/static/customers.html
- **Analytics**: http://127.0.0.1:8000/static/analytics.html
- **Predictions**: http://127.0.0.1:8000/static/predictions.html
- **Settings**: http://127.0.0.1:8000/static/settings.html

### 6. Docker (All-in-One)

```bash
docker-compose up --build
# API:       http://localhost:5000
# Dashboard: http://localhost:8000
# MySQL:     localhost:3306
```

---

## 🧪 API Usage

### Health Check
```bash
curl http://localhost:5000/health
```

### Predict Churn for a Customer
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "C12345",
    "revenue": 1500.0,
    "monthly_charges": 85.5,
    "usage_frequency": 12,
    "complaints_count": 2,
    "payment_delays": 1,
    "gender": "Male",
    "seniorcitizen": "No",
    "contract": "Month-to-month"
  }'
```

**Response:**
```json
{
  "customer_id": "C12345",
  "churn_probability": 0.7234,
  "risk_bucket": "HIGH",
  "revenue": 1500.0,
  "expected_revenue_loss": 1085.10,
  "priority_score": 784.89
}
```

### Dashboard Summary
```bash
curl http://localhost:5000/api/dashboard/summary
```

### Top Priority Customers
```bash
curl http://localhost:5000/api/dashboard/priority_customers
```

---

## 📊 EDA Outputs

Running `python src/eda.py` generates 8 plots in `reports/figures/` and a `reports/business_insights.csv`. No Jupyter required.

| Plot | Business Insight |
|------|-----------------|
| Churn Distribution | Overall churn rate (pie + bar) |
| Churn by Contract | Which contract type loses the most customers |
| Tenure vs Churn | Do new customers churn faster? |
| Monthly Charges Boxplot | Revenue profile of churners |
| Complaints & Payment Delays | Behavioural signals predicting churn |
| Correlation Heatmap | Feature relationships with churn |
| Revenue at Risk | Dollar value of the churn problem |
| High-Risk Profiles | What separates churners from retained customers |

See `reports/README.md` for full documentation of all outputs.

---

## 🔑 Key Outputs Explained

| Output | Formula | Use |
|--------|---------|-----|
| `churn_probability` | Model output | Individual risk score |
| `risk_bucket` | Low <40% / Medium 40–70% / High ≥70% | Segmentation |
| `expected_revenue_loss` | `churn_prob × revenue` | Financial impact |
| `priority_score` | `churn_prob × expected_revenue_loss` | Retention ranking |
| `clv_estimate` | `(revenue/tenure) × (1−prob) × avg_tenure` | Customer value proxy |

---

## 🏗️ DevOps

| Component | Status |
|-----------|--------|
| Docker containerisation | ✅ |
| Docker Compose (MySQL + API) | ✅ |
| CI/CD GitHub Actions | ✅ |
| CI/CD Jenkins Pipeline | ✅ |
| Performance gate (AUC ≥ 0.70) | ✅ |
| AWS ECR (Docker image registry) | ✅ |
| AWS ECS Fargate (cloud deployment) | ✅ |
| Auto-retraining trigger (weekly cron) | ✅ |

---

## ☁️ Deployment (Jenkins + AWS)

### End-to-End Flow

```
New data pushed to repo (or weekly cron fires)
        │
        ▼
  Jenkins triggers pipeline
        │
        ▼
  run_pipeline.py (ingest → clean → features → EDA → train → evaluate)
        │
        ▼
  Metrics gate: ROC-AUC ≥ 0.70?
     YES │          NO → Build fails, no deployment
        ▼
  Docker build (API + Webapp images)
        │
        ▼
  Push to AWS ECR
        │
        ▼
  Update AWS ECS Fargate → New containers go live
```

### Jenkins Pipeline (`Jenkinsfile`)

7 automated stages:

| Stage | What it does |
|-------|-------------|
| Checkout | Pull code from GitHub |
| Install Dependencies | `pip install -r requirements.txt` |
| Run ML Pipeline | `python run_pipeline.py` (full 8-step pipeline) |
| Metrics Gate | Fail build if ROC-AUC < 0.70 |
| Docker Build | Build API + Webapp images |
| Push to ECR | Push images to AWS ECR |
| Deploy to ECS | Update ECS service with new image |

**Auto-retraining**: Jenkins cron runs every Sunday at 2 AM automatically.

### AWS Setup (One-Time)

```bash
# 1. Create ECR repositories
chmod +x aws/ecr-setup.sh
./aws/ecr-setup.sh

# 2. Create ECS cluster + service
#    First, set your subnet/security group:
export SUBNET_IDS="subnet-xxxxxxxx,subnet-yyyyyyyy"
export SECURITY_GROUP="sg-xxxxxxxx"
chmod +x aws/ecs-service.sh
./aws/ecs-service.sh
```

### Jenkins Setup

1. Install Jenkins with Docker + AWS CLI on the build server
2. Install plugins: **Pipeline**, **Docker Pipeline**, **AWS Credentials**
3. Add credentials in Jenkins > Manage Credentials:
   - `AWS_ACCOUNT_ID` (Secret text)
   - `AWS_DEFAULT_REGION` (Secret text)
   - `aws-credentials` (AWS Credentials type)
4. Create a Pipeline job pointing to the `Jenkinsfile` in the repo

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit: `git commit -m 'Add your feature'`
4. Push: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📄 License

MIT License — see LICENSE file.

---

**Built with ❤️ for Data Science, Machine Learning, and DevOps**
