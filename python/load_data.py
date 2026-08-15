import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
from urllib.parse import quote_plus

# Load DB connection info from the .env file
#Env does not transfer over so we need to make a new file for ourselves to test code.
load_dotenv()

required_env_vars = ["DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT", "DB_NAME"]
missing_env_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_env_vars:
    raise SystemExit(
        f"Missing required environment variable(s): {', '.join(missing_env_vars)}. "
        "Copy python/.env.example to python/.env and fill in your DB credentials."
    )

db_user = os.getenv("DB_USER")
db_password = quote_plus(os.getenv("DB_PASSWORD"))
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

# Create the SQLAlchemy engine (the connection channel to the DB)
engine = create_engine(
    f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
)

# Read the raw CSV
df = pd.read_csv("data/Superstore.csv", encoding="utf-8-sig")

print("Raw data shape:", df.shape)
print(df.columns.tolist())

# ---------------------------
# 1. Extract data for the dim_customers table
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
# 2. Extract data for the dim_products table
# ---------------------------
products = df[[
    "Product ID", "Category", "Sub-Category", "Product Name"
]].drop_duplicates(subset="Product ID")

products.columns = ["product_id", "category", "sub_category", "product_name"]

# ---------------------------
# 3. Extract data for the fact_orders table
# ---------------------------
orders = df[[
    "Row ID", "Order ID", "Order Date", "Ship Date", "Ship Mode",
    "Customer ID", "Product ID", "Sales", "Quantity", "Discount", "Profit"
]]

orders.columns = [
    "row_id", "order_id", "order_date", "ship_date", "ship_mode",
    "customer_id", "product_id", "sales", "quantity", "discount", "profit"
]

# Convert date format (MM/DD/YYYY -> DATE)
orders["order_date"] = pd.to_datetime(orders["order_date"])
orders["ship_date"] = pd.to_datetime(orders["ship_date"])

# ---------------------------
# Load into the DB (order matters: customers/products first, then orders)
# ---------------------------
customers.to_sql("dim_customers", engine, if_exists="append", index=False)
print(f"dim_customers: {len(customers)} rows loaded")

products.to_sql("dim_products", engine, if_exists="append", index=False)
print(f"dim_products: {len(products)} rows loaded")

orders.to_sql("fact_orders", engine, if_exists="append", index=False)
print(f"fact_orders: {len(orders)} rows loaded")

print("All done!")
