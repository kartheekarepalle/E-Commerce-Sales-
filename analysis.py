import pandas as pd
from sqlalchemy import create_engine

print("📊 Starting OLAP Analysis...")

# Connect to database
engine = create_engine('sqlite:///ecommerce_dw.db')

# ------------------------------
# TOP 5 PRODUCTS
# ------------------------------

query1 = """
SELECT p.product_name, SUM(f.sales_amount) as total_sales
FROM Sales_Fact f
JOIN Product_Dim p ON f.product_id = p.product_id
GROUP BY p.product_name
ORDER BY total_sales DESC
LIMIT 5
"""

top_products = pd.read_sql(query1, engine)

print("\n🔥 Top 5 Selling Products:")
print(top_products)


# ------------------------------
# TOP REGIONS
# ------------------------------

query2 = """
SELECT c.region, SUM(f.sales_amount) as total_sales
FROM Sales_Fact f
JOIN Customer_Dim c ON f.customer_id = c.customer_id
GROUP BY c.region
ORDER BY total_sales DESC
"""

top_regions = pd.read_sql(query2, engine)

print("\n🌍 Sales by Region:")
print(top_regions)

query3 = """
SELECT d.year, d.month, SUM(f.sales_amount) as total_sales
FROM Sales_Fact f
JOIN Date_Dim d ON f.date_id = d.date_id
GROUP BY d.year, d.month
ORDER BY d.year, d.month
"""

monthly_sales = pd.read_sql(query3, engine)

print("\n📈 Monthly Sales Trend:")
print(monthly_sales.head())

query4 = """
SELECT p.category, SUM(f.sales_amount) as total_sales
FROM Sales_Fact f
JOIN Product_Dim p ON f.product_id = p.product_id
GROUP BY p.category
ORDER BY total_sales DESC
"""

category_sales = pd.read_sql(query4, engine)

print("\n📦 Sales by Category:")
print(category_sales)

import matplotlib.pyplot as plt

plt.figure()
plt.bar(category_sales['category'], category_sales['total_sales'])
plt.title("Sales by Category")
plt.show()
