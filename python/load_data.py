import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
from urllib.parse import quote_plus

# .env 파일에서 DB 접속 정보 불러오기
#Env does not transfer over so we need to make a new file for ourselves to test code.
load_dotenv()

db_user = os.getenv("DB_USER")
db_password = quote_plus(os.getenv("DB_PASSWORD"))
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

# SQLAlchemy 엔진 생성 (DB 연결 통로)
engine = create_engine(
    f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
)

# 원본 CSV 읽기
df = pd.read_csv("data/Superstore.csv", encoding="utf-8-sig")

print("원본 데이터 shape:", df.shape)
print(df.columns.tolist())

# ---------------------------
# 1. dim_customers 테이블용 데이터 추출
# ---------------------------
customers = df[[
    "Customer ID", "Customer Name", "Segment",
    "Country", "City", "State", "Postal Code", "Region"
]].drop_duplicates(subset="Customer ID")

customers.columns = [
    "customer_id", "customer_name", "segment",
    "country", "city", "state", "postal_code", "region"
]

# ---------------------------
# 2. dim_products 테이블용 데이터 추출
# ---------------------------
products = df[[
    "Product ID", "Category", "Sub-Category", "Product Name"
]].drop_duplicates(subset="Product ID")

products.columns = ["product_id", "category", "sub_category", "product_name"]

# ---------------------------
# 3. fact_orders 테이블용 데이터 추출
# ---------------------------
orders = df[[
    "Row ID", "Order ID", "Order Date", "Ship Date", "Ship Mode",
    "Customer ID", "Product ID", "Sales", "Quantity", "Discount", "Profit"
]]

orders.columns = [
    "row_id", "order_id", "order_date", "ship_date", "ship_mode",
    "customer_id", "product_id", "sales", "quantity", "discount", "profit"
]

# 날짜 형식 변환 (MM/DD/YYYY -> DATE)
orders["order_date"] = pd.to_datetime(orders["order_date"])
orders["ship_date"] = pd.to_datetime(orders["ship_date"])

# ---------------------------
# DB에 적재 (순서 중요: customers/products 먼저, orders 나중)
# ---------------------------
customers.to_sql("dim_customers", engine, if_exists="append", index=False)
print(f"dim_customers: {len(customers)}행 적재 완료")

products.to_sql("dim_products", engine, if_exists="append", index=False)
print(f"dim_products: {len(products)}행 적재 완료")

orders.to_sql("fact_orders", engine, if_exists="append", index=False)
print(f"fact_orders: {len(orders)}행 적재 완료")

print("전체 완료!")
