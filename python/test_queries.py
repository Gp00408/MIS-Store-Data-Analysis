#Needed to test if the code works in vs code.

import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
from urllib.parse import quote_plus

load_dotenv()
db_user = os.getenv("DB_USER")
db_password = quote_plus(os.getenv("DB_PASSWORD"))
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

engine = create_engine(
    f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
)

queries = {
    "1. Monthly Sales Trend": """
        SELECT DATE_TRUNC('month', order_date)::DATE AS order_month,
               COUNT(DISTINCT order_id) AS order_count,
               SUM(sales) AS total_sales,
               SUM(profit) AS total_profit,
               ROUND((SUM(profit) / NULLIF(SUM(sales), 0) * 100)::numeric, 2) AS profit_margin_pct
        FROM fact_orders
        GROUP BY DATE_TRUNC('month', order_date)
        ORDER BY order_month;
    """,
    "2. Profit Margin by Category": """
        SELECT p.category,
               SUM(f.sales) AS total_sales,
               SUM(f.profit) AS total_profit,
               ROUND((SUM(f.profit) / NULLIF(SUM(f.sales), 0) * 100)::numeric, 2) AS profit_margin_pct
        FROM fact_orders f
        JOIN dim_products p ON f.product_id = p.product_id
        GROUP BY p.category
        ORDER BY profit_margin_pct DESC;
    """,
    "3. Regional Performance": """
        SELECT c.region,
               COUNT(DISTINCT f.order_id) AS order_count,
               SUM(f.sales) AS total_sales,
               SUM(f.profit) AS total_profit
        FROM fact_orders f
        JOIN dim_customers c ON f.customer_id = c.customer_id
        GROUP BY c.region
        ORDER BY total_sales DESC;
    """,
}

for label, query in queries.items():
    print(f"\n===== {label} =====")
    df = pd.read_sql(text(query), engine)
    print(df)
