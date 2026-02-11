print("🚀 ETL Script Started...")

import pandas as pd
from sqlalchemy import create_engine
import os

try:
    # --------------------------
    # STEP 1: READ DATA
    # --------------------------

    file_path = "data/train.csv"

    if not os.path.exists(file_path):
        raise FileNotFoundError("train.csv not found inside data folder")

    df = pd.read_csv(file_path, encoding="latin1")

    print("✅ Dataset Loaded Successfully")
    print("Total Rows:", len(df))

    # --------------------------
    # STEP 2: TRANSFORM DATA
    # --------------------------

    # Correct Date Conversion
    df['Order Date'] = pd.to_datetime(
        df['Order Date'],
        dayfirst=True,
        errors='coerce'
    )

    # Remove invalid dates
    df = df.dropna(subset=['Order Date'])

    # Remove duplicates
    df = df.drop_duplicates()

    print("✅ Data Cleaned")

    # --------------------------
    # STEP 3: DATE DIMENSION
    # --------------------------

    date_dim = df[['Order Date']].drop_duplicates().copy()
    date_dim['year'] = date_dim['Order Date'].dt.year
    date_dim['month'] = date_dim['Order Date'].dt.month
    date_dim['quarter'] = date_dim['Order Date'].dt.quarter
    date_dim = date_dim.reset_index(drop=True)
    date_dim['date_id'] = date_dim.index + 1

    print("✅ Date Dimension Created")

    df = df.merge(date_dim, on='Order Date')

    # --------------------------
    # STEP 4: PRODUCT DIMENSION
    # --------------------------

    product_dim = df[['Product ID', 'Product Name', 'Category']].drop_duplicates().copy()
    product_dim.columns = ['product_id', 'product_name', 'category']

    print("✅ Product Dimension Created")

    # --------------------------
    # STEP 5: CUSTOMER DIMENSION
    # --------------------------

    customer_dim = df[['Customer ID', 'Customer Name', 'City', 'State', 'Region']].drop_duplicates().copy()
    customer_dim.columns = ['customer_id', 'customer_name', 'city', 'state', 'region']

    print("✅ Customer Dimension Created")

    # --------------------------
    # STEP 6: FACT TABLE
    # --------------------------

    sales_fact = df[['Order ID', 'Product ID', 'Customer ID', 'date_id', 'Sales']].copy()
    sales_fact.columns = ['order_id', 'product_id', 'customer_id', 'date_id', 'sales_amount']

    print("✅ Sales Fact Table Created")

    # --------------------------
    # STEP 7: LOAD INTO DATABASE
    # --------------------------

    engine = create_engine('sqlite:///ecommerce_dw.db')

    product_dim.to_sql("Product_Dim", engine, if_exists='replace', index=False)
    customer_dim.to_sql("Customer_Dim", engine, if_exists='replace', index=False)
    date_dim.to_sql("Date_Dim", engine, if_exists='replace', index=False)
    sales_fact.to_sql("Sales_Fact", engine, if_exists='replace', index=False)

    print("🎉 Data Warehouse Created Successfully!")
    print("Database File: ecommerce_dw.db")

except Exception as e:
    print("❌ Error Occurred:", e)
