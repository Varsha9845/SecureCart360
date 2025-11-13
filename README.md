# SecureCart360  
A data-driven mini e-commerce risk intelligence system built using AI-generated synthetic data, SQLite, and SQL analytics.
___________________________________________________________________________________________________________________________________________________________

## Project Overview  
SecureCart360 demonstrates:
- AI-assisted data generation (5 CSV files)
- Data ingestion pipeline into SQLite
- Audit-ready relational schema
- Fraud signal modeling (risk scoring)
- SQL joins for multi-table analytics
- Visual insights for risk patterns
___________________________________________________________________________________________________________________________________________________________

##  Project Structure
1. data/ → 5 synthetic CSVs
2. insights/ → Generated charts (fraud_distribution and high_risk_users pngs)
3. scripts/ → Python ETL + insights
4. sql/join_report.sql→ Fraud report view
5. ecommerce.db → SQLite database
___________________________________________________________________________________________________________________________________________________________

##  How to Run

1) Load data into SQLite -> python3 scripts/load_into_sqlite.py
2) Run SQL fraud report -> sqlite3 ecommerce.db ".read sql/join_report.sql"
3) Generate charts -> python3 scripts/insights.py
___________________________________________________________________________________________________________________________________________________________

## Outputs

1. fraud_distribution.png

2. high_risk_users.png

Both available in the insights/ folder.
___________________________________________________________________________________________________________________________________________________________

## Key Features

1. **Synthetic E-Commerce Dataset**  
   Relational dataset with customers, orders, products, order items, and fraud signals.

2. **Fraud Scoring Engine**  
   Risk classification using:  
   - payment_risk_score  
   - device_change_flag  
   - high_value_flag  

3. **SQL Fraud Analytics View**  
  A consolidated SQL view (`vw_order_fraud_report`) combining all tables with computed `fraud_risk_level`.

4. **Automated Visualizations**  
   Includes charts for:  
   - Fraud risk distribution  
   - Top high-risk customers  

5. **Simple, Reproducible ETL Workflow**  
   Designed to be fully transparent and easy to run for reviewers.

___________________________________________________________________________________________________________________________________________________________

## Outputs

### Fraud Risk Distribution
![Fraud Distribution]([Fraud risk distribution.png](https://github.com/Varsha9845/SecureCart360/blob/main/Fraud%20risk%20distribution.png?raw=true))

### High-Risk Users
![High Risk Users]([High risk users.png](https://github.com/Varsha9845/SecureCart360/blob/main/High%20risk%20users.png?raw=true))

___________________________________________________________________________________________________________________________________________________________

## Tools Used
- Python  
- SQLite  
- Pandas  
- Matplotlib  
- Cursor (for AI-based prompt generation)



