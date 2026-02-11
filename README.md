PROJECT TITLE:
E-Commerce Sales Data Warehouse

---

PROJECT OBJECTIVE:
To design and implement a Data Warehouse system for analyzing
E-Commerce sales trends using ETL, Star Schema, and OLAP techniques.

The system identifies:
- Top Selling Products
- Top Performing Regions
- Monthly Sales Trends
- Category-wise Sales Performance

---

TOOLS AND TECHNOLOGIES USED:

- Python
- Pandas
- SQLite
- SQL (OLAP Queries)
- Matplotlib (for visualization)

---

DATA SOURCE:

Kaggle Superstore Dataset (train.csv)

Columns used:
- Order ID
- Order Date
- Customer ID
- Customer Name
- City
- State
- Region
- Product ID
- Product Name
- Category
- Sales

---

PROJECT ARCHITECTURE:

Raw CSV Dataset
        ↓
ETL Process (Extract, Transform, Load)
        ↓
Star Schema Data Warehouse (SQLite)
        ↓
OLAP Queries
        ↓
Business Insights & Visualization

---

STAR SCHEMA DESIGN:

FACT TABLE:
Sales_Fact
- order_id
- product_id (FK)
- customer_id (FK)
- date_id (FK)
- sales_amount

DIMENSION TABLES:

Product_Dim
- product_id
- product_name
- category

Customer_Dim
- customer_id
- customer_name
- city
- state
- region

Date_Dim
- date_id
- order_date
- year
- month
- quarter

---

ETL PROCESS:

1. Extract:
   - Read raw data from train.csv

2. Transform:
   - Convert date format
   - Remove duplicates
   - Create Date Dimension
   - Prepare Fact and Dimension tables

3. Load:
   - Store tables into SQLite database (ecommerce_dw.db)

---

OLAP ANALYSIS PERFORMED:

1. Top 5 Selling Products
2. Sales by Region
3. Monthly Sales Trend
4. Sales by Category

---

BUSINESS INSIGHTS:

- West region generates highest revenue.
- Technology category contributes most to sales.
- Canon imageCLASS 2200 Advanced Copier is top selling product.
- Sales trends show seasonal fluctuations.

---

CONCLUSION:

This project successfully demonstrates the implementation
of a Data Warehouse using Star Schema and ETL techniques.
It enables analytical reporting and supports business decision-making
through OLAP queries.

---

END OF PROJECT
