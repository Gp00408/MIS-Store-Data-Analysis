-- ============================================================
-- analysis_queries.sql
-- Round 3: SQL analysis queries on the loaded data
-- (monthly sales, profit margin by category, regional performance, etc.)
-- Schema: dim_customers / dim_products / fact_orders
-- ============================================================


-- ------------------------------------------------------------
-- 1. Monthly Sales Trend
-- ------------------------------------------------------------
SELECT
    DATE_TRUNC('month', order_date)::DATE AS order_month,
    COUNT(DISTINCT order_id)              AS order_count,
    SUM(sales)                            AS total_sales,
    SUM(profit)                           AS total_profit,
    ROUND(SUM(profit) / NULLIF(SUM(sales), 0) * 100, 2) AS profit_margin_pct
FROM fact_orders
GROUP BY DATE_TRUNC('month', order_date)
ORDER BY order_month;


-- ------------------------------------------------------------
-- 1-1. Month-over-Month Sales Growth
-- ------------------------------------------------------------
WITH monthly_sales AS (
    SELECT
        DATE_TRUNC('month', order_date)::DATE AS order_month,
        SUM(sales) AS total_sales
    FROM fact_orders
    GROUP BY DATE_TRUNC('month', order_date)
)
SELECT
    order_month,
    total_sales,
    LAG(total_sales) OVER (ORDER BY order_month) AS prev_month_sales,
    ROUND(
        (total_sales - LAG(total_sales) OVER (ORDER BY order_month))
        / NULLIF(LAG(total_sales) OVER (ORDER BY order_month), 0) * 100
    , 2) AS mom_growth_pct
FROM monthly_sales
ORDER BY order_month;


-- ------------------------------------------------------------
-- 2. Profit Margin by Category
-- ------------------------------------------------------------
SELECT
    p.category,
    COUNT(*)                              AS order_line_count,
    SUM(f.sales)                          AS total_sales,
    SUM(f.profit)                         AS total_profit,
    ROUND(SUM(f.profit) / NULLIF(SUM(f.sales), 0) * 100, 2) AS profit_margin_pct
FROM fact_orders f
JOIN dim_products p ON f.product_id = p.product_id
GROUP BY p.category
ORDER BY profit_margin_pct DESC;


-- ------------------------------------------------------------
-- 2-1. Profit Margin by Sub-Category
-- ------------------------------------------------------------
SELECT
    p.category,
    p.sub_category,
    SUM(f.sales)   AS total_sales,
    SUM(f.profit)  AS total_profit,
    ROUND(SUM(f.profit) / NULLIF(SUM(f.sales), 0) * 100, 2) AS profit_margin_pct
FROM fact_orders f
JOIN dim_products p ON f.product_id = p.product_id
GROUP BY p.category, p.sub_category
ORDER BY p.category, profit_margin_pct DESC;


-- ------------------------------------------------------------
-- 3. Regional Performance
-- ------------------------------------------------------------
SELECT
    c.region,
    COUNT(DISTINCT f.order_id)            AS order_count,
    COUNT(DISTINCT f.customer_id)         AS customer_count,
    SUM(f.sales)                          AS total_sales,
    SUM(f.profit)                         AS total_profit,
    ROUND(SUM(f.profit) / NULLIF(SUM(f.sales), 0) * 100, 2) AS profit_margin_pct
FROM fact_orders f
JOIN dim_customers c ON f.customer_id = c.customer_id
GROUP BY c.region
ORDER BY total_sales DESC;


-- ------------------------------------------------------------
-- 3-1. Region x Category Cross Performance
-- ------------------------------------------------------------
SELECT
    c.region,
    p.category,
    SUM(f.sales)   AS total_sales,
    SUM(f.profit)  AS total_profit
FROM fact_orders f
JOIN dim_customers c ON f.customer_id = c.customer_id
JOIN dim_products  p ON f.product_id  = p.product_id
GROUP BY c.region, p.category
ORDER BY c.region, total_sales DESC;


-- ------------------------------------------------------------
-- 4. Performance by Customer Segment
-- ------------------------------------------------------------
SELECT
    c.segment,
    COUNT(DISTINCT c.customer_id)         AS customer_count,
    SUM(f.sales)                          AS total_sales,
    SUM(f.profit)                         AS total_profit,
    ROUND(SUM(f.sales) / NULLIF(COUNT(DISTINCT c.customer_id), 0), 2) AS avg_sales_per_customer
FROM fact_orders f
JOIN dim_customers c ON f.customer_id = c.customer_id
GROUP BY c.segment
ORDER BY total_sales DESC;


-- ------------------------------------------------------------
-- 5. Top 10 Customers by Sales
-- ------------------------------------------------------------
SELECT
    c.customer_id,
    c.customer_name,
    c.segment,
    SUM(f.sales)  AS total_sales,
    SUM(f.profit) AS total_profit
FROM fact_orders f
JOIN dim_customers c ON f.customer_id = c.customer_id
GROUP BY c.customer_id, c.customer_name, c.segment
ORDER BY total_sales DESC
LIMIT 10;


-- ------------------------------------------------------------
-- 6. Loss-Making Orders — candidates for outlier detection
-- ------------------------------------------------------------
SELECT
    f.row_id,
    f.order_id,
    f.order_date,
    p.category,
    p.sub_category,
    f.sales,
    f.discount,
    f.profit
FROM fact_orders f
JOIN dim_products p ON f.product_id = p.product_id
WHERE f.profit < 0
ORDER BY f.profit ASC;


-- ------------------------------------------------------------
-- 7. Discount vs Profitability
-- ------------------------------------------------------------
SELECT
    CASE
        WHEN discount = 0            THEN '0%'
        WHEN discount <= 0.10        THEN '0-10%'
        WHEN discount <= 0.20        THEN '10-20%'
        WHEN discount <= 0.30        THEN '20-30%'
        ELSE '30%+'
    END AS discount_bucket,
    COUNT(*)                              AS order_line_count,
    SUM(sales)                            AS total_sales,
    SUM(profit)                           AS total_profit,
    ROUND(AVG(profit), 2)                 AS avg_profit_per_line
FROM fact_orders
GROUP BY 1
ORDER BY 1;


-- ------------------------------------------------------------
-- 8. Performance by Ship Mode
-- ------------------------------------------------------------
SELECT
    ship_mode,
    COUNT(*)                              AS order_line_count,
    ROUND(AVG(ship_date - order_date), 1) AS avg_ship_days,
    SUM(sales)                            AS total_sales,
    SUM(profit)                           AS total_profit
FROM fact_orders
GROUP BY ship_mode
ORDER BY order_line_count DESC;


-- ------------------------------------------------------------
-- 9. Year x Category Sales — pre-pivoted for Power BI
-- ------------------------------------------------------------
SELECT
    EXTRACT(YEAR FROM f.order_date)::INT AS order_year,
    p.category,
    SUM(f.sales)   AS total_sales,
    SUM(f.profit)  AS total_profit
FROM fact_orders f
JOIN dim_products p ON f.product_id = p.product_id
GROUP BY EXTRACT(YEAR FROM f.order_date), p.category
ORDER BY order_year, p.category;
