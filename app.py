import streamlit as st
import pandas as pd
import plotly.express as px
import time
import re
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sqlalchemy import create_engine

st.set_page_config(layout="wide")

# ------------------------------
# CLEAN PROFESSIONAL UI STYLE
# ------------------------------
st.markdown("""
<style>
.stApp {
    background-color: #f4f6f9;
}
.block-container {
    padding-top: 2rem;
}
h1, h2, h3 {
    color: #1f2937;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------
# TITLE
# ------------------------------
st.title("📊 Universal Sales Analysis System")
st.caption("Dynamic ETL, OLAP & Algorithm Performance Comparison Platform")

# ------------------------------
# SESSION HISTORY
# ------------------------------
if "history" not in st.session_state:
    st.session_state.history = {}

def detect_column(keywords, df):
    for col in df.columns:
        for key in keywords:
            if key.lower() in col.lower():
                return col
    return None

# ------------------------------
# FILE UPLOAD
# ------------------------------
uploaded_file = st.file_uploader("Upload Sales Dataset (CSV)", type=["csv"])

if uploaded_file is not None:

    try:
        chunks = pd.read_csv(uploaded_file, encoding="latin1", chunksize=300000)
        df = pd.concat(chunks)
    except:
        df = pd.read_csv(uploaded_file, encoding="latin1")

    df.columns = df.columns.str.strip()

    dataset_name = uploaded_file.name

    # ---------------- COLUMN DETECTION ----------------
    product_col = detect_column(["product", "description", "item"], df)
    sales_col = detect_column(["sales", "revenue", "amount"], df)

    if not sales_col:
        quantity_col = detect_column(["quantity"], df)
        price_col = detect_column(["price", "unitprice"], df)

        if quantity_col and price_col:
            df["Sales"] = pd.to_numeric(df[quantity_col], errors="coerce") * \
                          pd.to_numeric(df[price_col], errors="coerce")
            sales_col = "Sales"
        else:
            st.error("This dataset does not contain valid sales transaction data.")
            st.stop()

    if not product_col:
        st.error("Product column not detected.")
        st.stop()

    # ================= SQL =================
    start_sql = time.time()
    engine = create_engine("sqlite:///:memory:")
    df.to_sql("sales", engine, index=False, if_exists="replace")

    sql_query = f"""
    SELECT `{product_col}`, SUM(`{sales_col}`) as total_sales
    FROM sales
    GROUP BY `{product_col}`
    ORDER BY total_sales DESC
    LIMIT 5
    """

    sql_result = pd.read_sql(sql_query, engine)
    sql_time = time.time() - start_sql

    # ================= PANDAS =================
    start_pd = time.time()
    pandas_result = (
        df.groupby(product_col)[sales_col]
        .sum()
        .sort_values(ascending=False)
        .head(5)
        .reset_index()
    )
    pandas_time = time.time() - start_pd

    # ================= ML =================
    start_ml = time.time()
    numeric_col = detect_column(["quantity", "price", "postal", "code"], df)
    mse = 0

    if numeric_col:
        df[numeric_col] = df[numeric_col].astype(str)
        df[numeric_col] = df[numeric_col].apply(lambda x: re.sub(r"[^0-9.]", "", x))
        df[numeric_col] = pd.to_numeric(df[numeric_col], errors="coerce")

        ml_df = df[[numeric_col, sales_col]].dropna()

        if len(ml_df) > 100:
            X = ml_df[[numeric_col]]
            y = ml_df[sales_col]

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            model = LinearRegression()
            model.fit(X_train, y_train)
            predictions = model.predict(X_test)
            mse = mean_squared_error(y_test, predictions)

    ml_time = time.time() - start_ml

    # ---------------- SAVE TO HISTORY ----------------
    st.session_state.history[dataset_name] = {
        "sql": sql_result,
        "pandas": pandas_result,
        "sql_time": sql_time,
        "pandas_time": pandas_time,
        "ml_time": ml_time,
        "mse": mse
    }

# ------------------------------
# HISTORY SIDEBAR
# ------------------------------
if st.session_state.history:

    st.sidebar.header("📂 Dataset History")
    selected_dataset = st.sidebar.radio(
        "Select Dataset",
        list(st.session_state.history.keys())
    )

    results = st.session_state.history[selected_dataset]

    st.success(f"Showing Results for: {selected_dataset}")

    # ---------------- KPI METRICS ----------------
    col1, col2, col3 = st.columns(3)

    col1.metric("SQL Time (sec)", f"{results['sql_time']:.6f}")
    col2.metric("Pandas Time (sec)", f"{results['pandas_time']:.6f}")
    col3.metric("ML Time (sec)", f"{results['ml_time']:.6f}")

    # ---------------- SQL GRAPH ----------------
    st.markdown("### Top 5 Products – SQL")
    sql_df = results["sql"].copy()
    sql_df["Short"] = sql_df.iloc[:, 0].astype(str).str[:25] + "..."

    fig_sql = px.bar(
        sql_df,
        y="Short",
        x="total_sales",
        orientation="h",
        color="total_sales",
        color_continuous_scale="Blues"
    )
    fig_sql.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig_sql, use_container_width=True)

    # ---------------- PANDAS GRAPH ----------------
    st.markdown("### Top 5 Products – Pandas")
    pandas_df = results["pandas"].copy()
    pandas_df["Short"] = pandas_df.iloc[:, 0].astype(str).str[:25] + "..."

    fig_pd = px.bar(
        pandas_df,
        y="Short",
        x=pandas_df.columns[1],
        orientation="h",
        color=pandas_df.columns[1],
        color_continuous_scale="Greens"
    )
    fig_pd.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig_pd, use_container_width=True)

    # ---------------- EXECUTION COMPARISON ----------------
    st.markdown("### Algorithm Execution Comparison")

    comparison = pd.DataFrame({
        "Algorithm": ["SQL", "Pandas", "Linear Regression"],
        "Execution Time (seconds)": [
            results["sql_time"],
            results["pandas_time"],
            results["ml_time"]
        ]
    })

    st.dataframe(comparison)

    fig_compare = px.bar(
        comparison,
        x="Algorithm",
        y="Execution Time (seconds)",
        color="Algorithm",
        text="Execution Time (seconds)"
    )
    fig_compare.update_traces(texttemplate='%{text:.6f}', textposition='outside')
    st.plotly_chart(fig_compare, use_container_width=True)

    # ---------------- ANALYSIS ----------------
    fastest = comparison.sort_values("Execution Time (seconds)").iloc[0]["Algorithm"]

    st.markdown("### Performance Interpretation")

    st.write(f"""
    Based on execution benchmarking, **{fastest}** achieved the lowest computational time.

    The difference in performance is influenced by:
    • In-memory processing efficiency  
    • Engine overhead (SQL vs Pandas)  
    • Dataset size and structure  
    • Model training complexity (for ML)  

    This comparison reflects execution efficiency, not predictive accuracy.
    """)

    if results["mse"] != 0:
        st.write(f"Machine Learning Mean Squared Error: {results['mse']:.2f}")
