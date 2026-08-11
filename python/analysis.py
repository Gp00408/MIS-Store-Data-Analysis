import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from dotenv import load_dotenv
from urllib.parse import quote_plus
import os
import json

load_dotenv()

db_user = os.getenv("DB_USER")
db_password = quote_plus(os.getenv("DB_PASSWORD"))
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

engine = create_engine(
    f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
)

# ============================================================
# 1. 월별 매출/이익 데이터 가져오기 
# ============================================================
monthly_query = """
SELECT
    DATE_TRUNC('month', order_date)::DATE AS order_month,
    SUM(sales)  AS total_sales,
    SUM(profit) AS total_profit
FROM fact_orders
GROUP BY DATE_TRUNC('month', order_date)
ORDER BY order_month;
"""
monthly = pd.read_sql(monthly_query, engine)

# ============================================================
# 2. Z-score 기반 이상치 탐지 (월별 매출/이익)
# ============================================================
def add_zscore(df, col):
    mean = df[col].mean()
    std = df[col].std()
    df[f"{col}_zscore"] = (df[col] - mean) / std
    df[f"{col}_is_outlier"] = df[f"{col}_zscore"].abs() > 2  # 임계값 2
    return df

monthly = add_zscore(monthly, "total_sales")
monthly = add_zscore(monthly, "total_profit")

# ============================================================
# 3. MoM(전월 대비) / YoY(전년 동월 대비) 성장률
# ============================================================
monthly["order_month"] = pd.to_datetime(monthly["order_month"])
monthly = monthly.sort_values("order_month").reset_index(drop=True)

monthly["mom_growth_pct"] = monthly["total_sales"].pct_change() * 100
monthly["yoy_growth_pct"] = monthly["total_sales"].pct_change(periods=12) * 100

# ============================================================
# 4. 개별 주문(order line) 단위 이익 이상치 탐지
# ============================================================
orders_query = """
SELECT row_id, order_id, order_date, sales, discount, profit
FROM fact_orders;
"""
orders = pd.read_sql(orders_query, engine)
orders = add_zscore(orders, "profit")

extreme_losses = orders[orders["profit_is_outlier"] & (orders["profit"] < 0)] \
    .sort_values("profit") \
    .head(10)

# ============================================================
# 5. 결과 출력 (터미널 확인용)
# ============================================================
print("=== 월별 이상치 탐지 결과 ===")
print(monthly[["order_month", "total_sales", "total_sales_is_outlier",
                "total_profit", "total_profit_is_outlier"]])

print("\n=== 가장 손해가 컸던 주문 TOP 10 (통계적 이상치) ===")
print(extreme_losses[["order_id", "order_date", "sales", "discount", "profit"]])

# ============================================================
# 6. GPT(Round 6)가 나중에 읽을 수 있게 요약 정보를 JSON으로 저장
# ============================================================
summary = {
    "total_months": len(monthly),
    "outlier_months_sales": monthly[monthly["total_sales_is_outlier"]]["order_month"]
        .dt.strftime("%Y-%m").tolist(),
    "outlier_months_profit": monthly[monthly["total_profit_is_outlier"]]["order_month"]
        .dt.strftime("%Y-%m").tolist(),
    "latest_month": monthly.iloc[-1]["order_month"].strftime("%Y-%m"),
    "latest_mom_growth_pct": round(monthly.iloc[-1]["mom_growth_pct"], 2)
        if pd.notna(monthly.iloc[-1]["mom_growth_pct"]) else None,
    "latest_yoy_growth_pct": round(monthly.iloc[-1]["yoy_growth_pct"], 2)
        if pd.notna(monthly.iloc[-1]["yoy_growth_pct"]) else None,
    "top_10_worst_orders": extreme_losses[["order_id", "profit"]].to_dict(orient="records"),
}

os.makedirs("data/processed", exist_ok=True)
with open("data/processed/analysis_summary.json", "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)

print("\n분석 완료! 요약 결과가 data/processed/analysis_summary.json 에 저장됐어요.")