-- Customer dimension table
CREATE TABLE dim_customers (
    customer_id     VARCHAR(20) PRIMARY KEY,
    customer_name   VARCHAR(100),
    segment         VARCHAR(50),
    country         VARCHAR(50),
    city            VARCHAR(50),
    state           VARCHAR(50),
    postal_code     VARCHAR(10),
    region          VARCHAR(20)
);

-- Product dimension table
CREATE TABLE dim_products (
    product_id      VARCHAR(20) PRIMARY KEY,
    category        VARCHAR(50),
    sub_category    VARCHAR(50),
    product_name    VARCHAR(255)
);

-- Order fact table (actual transaction data)
CREATE TABLE fact_orders (
    row_id          INT PRIMARY KEY,
    order_id        VARCHAR(20),
    order_date      DATE,
    ship_date       DATE,
    ship_mode       VARCHAR(30),
    customer_id     VARCHAR(20) REFERENCES dim_customers(customer_id),
    product_id      VARCHAR(20) REFERENCES dim_products(product_id),
    sales           NUMERIC(10,2),
    quantity        INT,
    discount        NUMERIC(4,2),
    profit          NUMERIC(10,2)
);