"""Generate simple insights PNGs for README preview
Run: python3 scripts/insights.py
"""
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os

os.makedirs('insights', exist_ok=True)

# Use your DB path
DB_PATH = 'ecommerce.db'

conn = sqlite3.connect(DB_PATH)

# 1) Fraud distribution using fraud_signals + computed risk level
q_fraud = """
SELECT
  CASE
    WHEN f.payment_risk_score >= 0.75 OR f.device_change_flag = 1 OR f.high_value_flag = 1 THEN 'HIGH'
    WHEN f.payment_risk_score BETWEEN 0.4 AND 0.75 THEN 'MEDIUM'
    ELSE 'LOW'
  END AS fraud_risk_level,
  COUNT(*) AS cnt
FROM fraud_signals f
JOIN orders o ON o.order_id = f.order_id
GROUP BY fraud_risk_level
ORDER BY CASE fraud_risk_level WHEN 'HIGH' THEN 3 WHEN 'MEDIUM' THEN 2 ELSE 1 END DESC;
"""
df = pd.read_sql(q_fraud, conn)

# Make sure df is not empty before plotting
if df.shape[0] == 0:
    print("No fraud data found. Run load_into_sqlite.py first.")
else:
    plt.figure(figsize=(6,4))
    df.plot.pie(y='cnt', labels=df['fraud_risk_level'], autopct='%1.1f%%', legend=False)
    plt.title('Fraud Risk Distribution')
    plt.ylabel('')
    plt.savefig('insights/fraud_distribution.png')
    plt.close()
    print("Saved insights/fraud_distribution.png")

# 2) Top high-risk customers — direct join (no view)
q_top_high = """
SELECT o.customer_id, c.full_name, COUNT(*) as high_risk_orders
FROM orders o
JOIN fraud_signals f ON o.order_id = f.order_id
JOIN customers c ON o.customer_id = c.customer_id
WHERE
  (CASE
     WHEN f.payment_risk_score >= 0.75 OR f.device_change_flag = 1 OR f.high_value_flag = 1 THEN 'HIGH'
     WHEN f.payment_risk_score BETWEEN 0.4 AND 0.75 THEN 'MEDIUM'
     ELSE 'LOW'
   END) = 'HIGH'
GROUP BY o.customer_id
ORDER BY high_risk_orders DESC
LIMIT 10;
"""
df2 = pd.read_sql(q_top_high, conn)

if df2.shape[0] == 0:
    print("No high-risk customers found.")
else:
    plt.figure(figsize=(8,4))
    plt.bar(df2['full_name'], df2['high_risk_orders'])
    plt.xticks(rotation=45, ha='right')
    plt.title('Top High-Risk Customers')
    plt.tight_layout()
    plt.savefig('insights/high_risk_users.png')
    plt.close()
    print("Saved insights/high_risk_users.png")

conn.close()
