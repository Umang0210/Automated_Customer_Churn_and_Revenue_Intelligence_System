-- CREATE DATABASE churn_intelligence;
-- USE churn_intelligence;
-- CREATE USER 'churn_user'@'localhost' IDENTIFIED BY 'StrongPassword123';
-- GRANT ALL PRIVILEGES ON churn_intelligence.* TO 'churn_user'@'localhost';
-- FLUSH PRIVILEGES;


-- CREATE TABLE customers_predictions (
--     customer_id VARCHAR(50) PRIMARY KEY,
--     churn_probability FLOAT NOT NULL,
--     risk_bucket ENUM('LOW', 'MEDIUM', 'HIGH') NOT NULL,
--     revenue FLOAT NOT NULL,
--     expected_revenue_loss FLOAT NOT NULL,
--     priority_score FLOAT NOT NULL,
--     model_version VARCHAR(20) NOT NULL,
--     prediction_timestamp DATETIME NOT NULL
-- );

-- CREATE TABLE business_kpis (
--     metric_name VARCHAR(50),
--     metric_value FLOAT,
--     generated_at DATETIME
-- );

-- CREATE TABLE segment_insights (
--     segment_type VARCHAR(50),
--     segment_value VARCHAR(50),
--     churn_rate FLOAT,
--     customer_count INT,
--     generated_at DATETIME
-- );


-- CREATE TABLE model_runs (
--     model_version VARCHAR(20),
--     roc_auc FLOAT,
--     precision_score FLOAT,
--     recall_score FLOAT,
--     training_rows INT,
--     run_timestamp DATETIME
-- );
SELECT * FROM business_kpis;
SELECT COUNT(*) FROM customers_predictions;
