-- join_report.sql
-- Builds a consolidated fraud analysis view and returns a high-risk report slice.

DROP VIEW IF EXISTS vw_order_fraud_report;
CREATE VIEW vw_order_fraud_report AS
SELECT
    o.order_id,
    o.order_date,
    o.customer_id,
    c.full_name AS full_name,
    c.country AS customer_country,
    o.order_total,
    o.payment_method,
    o.order_status,
    oi.item_id,
    oi.product_id,
    p.product_name,
    p.category AS product_category,
    oi.quantity,
    oi.unit_price,
    f.payment_risk_score,
    f.high_value_flag,
    f.device_change_flag,
    CASE
        WHEN (
            COALESCE(f.payment_risk_score, 0.0)
            + 0.25 * COALESCE(f.high_value_flag, 0)
            + 0.15 * COALESCE(f.device_change_flag, 0)
        ) > 1.0 THEN 1.0
        ELSE ROUND(
            COALESCE(f.payment_risk_score, 0.0)
            + 0.25 * COALESCE(f.high_value_flag, 0)
            + 0.15 * COALESCE(f.device_change_flag, 0)
        , 4)
    END AS fraud_risk_score,
    CASE
        WHEN (
            COALESCE(f.payment_risk_score, 0.0)
            + 0.25 * COALESCE(f.high_value_flag, 0)
            + 0.15 * COALESCE(f.device_change_flag, 0)
        ) >= 0.85 THEN 'CRITICAL'
        WHEN (
            COALESCE(f.payment_risk_score, 0.0)
            + 0.25 * COALESCE(f.high_value_flag, 0)
            + 0.15 * COALESCE(f.device_change_flag, 0)
        ) >= 0.60 THEN 'HIGH'
        WHEN (
            COALESCE(f.payment_risk_score, 0.0)
            + 0.25 * COALESCE(f.high_value_flag, 0)
            + 0.15 * COALESCE(f.device_change_flag, 0)
        ) >= 0.35 THEN 'MEDIUM'
        ELSE 'LOW'
    END AS fraud_risk_level
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.customer_id
LEFT JOIN order_items oi ON o.order_id = oi.order_id
LEFT JOIN products p ON oi.product_id = p.product_id
LEFT JOIN fraud_signals f ON o.order_id = f.order_id;

SELECT *
FROM vw_order_fraud_report
ORDER BY fraud_risk_score DESC, order_date DESC
LIMIT 25;
