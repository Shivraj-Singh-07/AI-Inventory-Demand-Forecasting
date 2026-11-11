
import streamlit as st
import pandas as pd
import numpy as np
import re

from io import BytesIO
from datetime import datetime

# MySQL connection helper already configured in config/database.py
from config.database import get_connection

from sklearn.linear_model import LinearRegression

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib.units import mm


# =====================================================
# 1. PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="InventoryIQ | Business Dashboard",
    page_icon="📦",
    layout="wide"
)

# Modern SaaS dashboard styling and navigation
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
:root { --navy:#101c36; --blue:#2563eb; --ink:#17233b; --muted:#5d6b82; }
html, body, [class*="css"] { font-family:Inter,sans-serif; }
.stApp { background:#f4f7fc; color:var(--ink); }
[data-testid="stHeader"] { background:rgba(244,247,252,.96); }
.block-container { max-width:1500px; padding-top:2rem; padding-bottom:4rem; }
[data-testid="stSidebar"] { background:linear-gradient(180deg,#101c36 0%,#142b50 100%); border-right:1px solid #23395e; }
[data-testid="stSidebar"] > div:first-child { padding-top:1.5rem; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,[data-testid="stSidebar"] label,[data-testid="stSidebar"] [data-testid="stCaptionContainer"] { color:#dbe7fb !important; }
.brand { font-size:1.55rem; font-weight:800; color:#fff; letter-spacing:-.7px; padding:8px 0 2px; }
.brand-sub { color:#9fb5d7; font-size:.68rem; letter-spacing:1.7px; text-transform:uppercase; margin-bottom:28px; }
.sidebar-label { color:#8fa8ce; font-size:.68rem; font-weight:800; letter-spacing:1.5px; text-transform:uppercase; margin:20px 0 10px; }
.sidebar-link { display:flex; align-items:center; gap:12px; padding:11px 13px; margin:5px 0; border-radius:11px; color:#dce8fb !important; text-decoration:none !important; font-size:.91rem; font-weight:600; border:1px solid transparent; transition:all .18s ease; }
.sidebar-link:hover { background:#203d6a; border-color:#31578d; color:#fff !important; }
.sidebar-link.active { background:linear-gradient(100deg,#2563eb,#3985f6); color:#fff !important; box-shadow:0 7px 18px rgba(37,99,235,.25); }
.sidebar-note { background:rgba(255,255,255,.07); border:1px solid rgba(255,255,255,.13); border-radius:14px; padding:14px; color:#dce8fb; font-size:.8rem; line-height:1.65; margin-top:22px; }
.sidebar-note b { color:#fff; }
.hero { position:relative; overflow:hidden; background:linear-gradient(112deg,#102449 0%,#174a91 58%,#2877d5 100%); padding:34px 38px; border-radius:22px; color:#fff; margin:2px 0 26px; box-shadow:0 14px 34px rgba(23,74,145,.18); }
.hero:after { content:""; position:absolute; width:310px; height:310px; border:1px solid rgba(255,255,255,.12); border-radius:50%; right:-70px; top:-160px; box-shadow:0 0 0 35px rgba(255,255,255,.035),0 0 0 75px rgba(255,255,255,.025); }
.hero h1 { color:#fff !important; font-size:2.15rem !important; line-height:1.18 !important; font-weight:800 !important; letter-spacing:-1px; margin:0 0 10px !important; }
.hero p { color:#e5efff !important; margin:0 !important; font-size:1rem; max-width:760px; line-height:1.6; }
.eyebrow { color:#b9d5ff; text-transform:uppercase; font-size:.7rem; letter-spacing:1.8px; font-weight:800; margin-bottom:12px; }
.hero-pill { display:inline-flex; margin-top:19px; padding:7px 12px; border:1px solid rgba(255,255,255,.25); border-radius:30px; color:#f1f6ff; background:rgba(255,255,255,.1); font-size:.76rem; font-weight:600; }
/* Explicit dark text on every light surface prevents low contrast. */
[data-testid="stAppViewContainer"] .main, [data-testid="stAppViewContainer"] .main * { color-scheme:light; }
[data-testid="stAppViewContainer"] .main h1,[data-testid="stAppViewContainer"] .main h2,[data-testid="stAppViewContainer"] .main h3,[data-testid="stAppViewContainer"] .main h4 { color:#17233b !important; font-weight:750 !important; letter-spacing:-.35px; }
[data-testid="stAppViewContainer"] .main p,[data-testid="stAppViewContainer"] .main li,[data-testid="stAppViewContainer"] .main label,[data-testid="stAppViewContainer"] .main [data-testid="stCaptionContainer"] { color:#35445d !important; }
.section-intro { color:#5d6b82 !important; font-size:.92rem; margin-top:-8px; margin-bottom:18px; line-height:1.55; }
[data-testid="stMetric"] { background:#fff !important; border:1px solid #e3eaf4; padding:19px 20px; border-radius:17px; box-shadow:0 5px 16px rgba(20,43,80,.045); min-height:112px; }
[data-testid="stMetricLabel"] { color:#62718a !important; font-weight:650 !important; }
[data-testid="stMetricValue"] { color:#142747 !important; font-weight:800 !important; }
[data-testid="stMetricDelta"] { font-weight:650 !important; }
div[data-testid="stVerticalBlockBorderWrapper"] { border:1px solid #e1e8f2 !important; border-radius:17px !important; background:#fff !important; box-shadow:0 5px 16px rgba(20,43,80,.035); }
[data-testid="stFileUploader"] { background:#f8fbff; border:1.5px dashed #8eadd8; border-radius:15px; padding:15px; }
[data-testid="stFileUploader"] * { color:#253957 !important; }
[data-testid="stDataFrame"],[data-testid="stTable"] { background:#fff; border:1px solid #e3eaf4; border-radius:13px; }
[data-testid="stAppViewContainer"] .main input,[data-testid="stAppViewContainer"] .main textarea,[data-testid="stAppViewContainer"] .main [data-baseweb="select"] > div,[data-testid="stAppViewContainer"] .main [data-testid="stChatInput"] textarea { background:#fff !important; color:#17233b !important; border-color:#cbd7e6 !important; }
[data-testid="stAppViewContainer"] .main input::placeholder,[data-testid="stAppViewContainer"] .main textarea::placeholder { color:#75839a !important; opacity:1 !important; }
.stButton > button,.stDownloadButton > button { border-radius:11px !important; min-height:43px; padding:0 18px; font-weight:700 !important; color:#1d3b68 !important; background:#fff !important; border:1px solid #cbd8e9 !important; box-shadow:0 2px 5px rgba(20,43,80,.04); transition:all .18s ease; }
.stButton > button:hover,.stDownloadButton > button:hover { border-color:#2563eb !important; color:#1d4ed8 !important; background:#f3f7ff !important; transform:translateY(-1px); }
.stButton > button[kind="primary"] { background:linear-gradient(100deg,#1d4ed8,#3478e5) !important; color:#fff !important; border-color:#1d4ed8 !important; box-shadow:0 6px 14px rgba(37,99,235,.2); }
.stButton > button[kind="primary"]:hover { background:#1745b5 !important; color:#fff !important; }
[data-testid="stAlert"] { border-radius:13px !important; }
[data-testid="stChatMessage"] { background:#fff !important; border:1px solid #e1e8f2 !important; border-radius:15px !important; }
[data-testid="stChatMessage"] p { color:#243650 !important; }
[data-testid="stChatInput"] { border:1px solid #cbd8e9 !important; border-radius:14px !important; background:#fff !important; }
hr { border-color:#e3eaf3 !important; }
@media (max-width:800px) { .block-container{padding:1rem 1rem 3rem;} .hero{padding:25px 22px;} .hero h1{font-size:1.65rem !important;} }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div class="brand">▦ InventoryIQ</div><div class="brand-sub">Intelligent inventory platform</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-label">Workspace navigation</div>', unsafe_allow_html=True)
    st.markdown('''
    <a class="sidebar-link active" href="#overview">▦ &nbsp; Overview</a>
    <a class="sidebar-link" href="#upload-data">⇧ &nbsp; Upload & analyse data</a>
    <a class="sidebar-link" href="#demand-forecast">⌁ &nbsp; Demand forecasting</a>
    <a class="sidebar-link" href="#inventory-results">◇ &nbsp; Inventory recommendations</a>
    <a class="sidebar-link" href="#forecast-history">◷ &nbsp; Forecast history</a>
    <a class="sidebar-link" href="#business-assistant">✳ &nbsp; Business assistant</a>
    ''', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-note"><b>Getting started</b><br>01 &nbsp; Upload your sales or inventory file<br>02 &nbsp; Review detected columns<br>03 &nbsp; Set supplier delivery time<br>04 &nbsp; Generate a demand forecast<br>05 &nbsp; Download your business report</div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#8fa8ce;font-size:.73rem;margin-top:18px">● Local chatbot &nbsp; · &nbsp; MySQL storage</div>', unsafe_allow_html=True)

st.markdown('''
<div id="overview" class="hero">
  <div class="eyebrow">INVENTORY INTELLIGENCE WORKSPACE</div>
  <h1>Make smarter inventory decisions.</h1>
  <p>Understand what is selling, see what needs attention and plan your next replenishment with clear, practical insights.</p>
  <span class="hero-pill">● &nbsp; Your business overview</span>
</div>
''', unsafe_allow_html=True)

# =====================================================
# 2. COLUMN ALIASES
# =====================================================

COLUMN_ALIASES = {

    "Product": [
        "product",
        "product_name",
        "item",
        "item_name",
        "sku"
    ],

    "Date": [
        "date",
        "sale_date",
        "order_date",
        "transaction_date"
    ],

    "Sales Quantity": [
        "units_sold",
        "quantity_sold",
        "sales_qty",
        "qty_sold",
        "quantity"
    ],

    "Current Stock": [
        "current_stock",
        "stock",
        "available_stock",
        "inventory",
        "stock_quantity"
    ],

    "Unit Price": [
        "unit_price",
        "selling_price",
        "price",
        "sale_price"
    ],

    "Unit Cost": [
        "unit_cost",
        "cost_price",
        "purchase_price"
    ],

    "Category": [
        "category",
        "product_category",
        "type"
    ],

    "Lead Time": [
        "lead_time",
        "lead_time_days",
        "delivery_days",
        "supplier_lead_time",
        "shipping_days"
    ]
}


# =====================================================
# 3. NORMALIZE COLUMN NAMES
# =====================================================

def normalize(name):

    name = str(name).strip().lower()

    return re.sub(r"[^a-z0-9]", "", name)


# =====================================================
# 4. AUTOMATIC COLUMN DETECTION
# =====================================================

def detect_columns(df):

    detected = {}

    normalized_columns = {
        normalize(col): col
        for col in df.columns
    }

    for role, aliases in COLUMN_ALIASES.items():

        for alias in aliases:

            key = normalize(alias)

            if key in normalized_columns:

                detected[role] = normalized_columns[key]
                break

    return detected


# =====================================================
# 5. DEMAND FORECASTING
# =====================================================

def forecast_demand(df, detected, default_lead_time, selected_models=None):

    product_col = detected["Product"]
    date_col = detected["Date"]
    sales_col = detected["Sales Quantity"]

    stock_col = detected.get("Current Stock")
    lead_col = detected.get("Lead Time")

    data = df.copy()

    data[date_col] = pd.to_datetime(
        data[date_col],
        errors="coerce"
    )

    data[sales_col] = pd.to_numeric(
        data[sales_col],
        errors="coerce"
    )

    data = data.dropna(
        subset=[product_col, date_col, sales_col]
    )

    data = data[data[sales_col] >= 0]

    if data.empty:
        return pd.DataFrame()

    if stock_col:

        data[stock_col] = pd.to_numeric(
            data[stock_col],
            errors="coerce"
        )

    if lead_col:

        data[lead_col] = pd.to_numeric(
            data[lead_col],
            errors="coerce"
        )

        data.loc[
            data[lead_col] <= 0,
            lead_col
        ] = np.nan

    data["Month"] = data[date_col].dt.to_period("M")

    monthly_sales = (
        data.groupby([product_col, "Month"])[sales_col]
        .sum()
        .reset_index()
    )

    results = []

    for product in monthly_sales[product_col].unique():

        product_data = monthly_sales[
            monthly_sales[product_col] == product
        ].sort_values("Month").copy()

        # At least 3 months of historical data
        if len(product_data) < 3:
            continue

        y = product_data[sales_col].astype(float).to_numpy()

        # Select the best validated model separately for each product.
        selected_model = (selected_models or {}).get(str(product), "Linear Regression")

        if selected_model == "Naive":
            prediction = float(y[-1])
        elif selected_model == "Moving Average (3 months)":
            prediction = float(np.mean(y[-3:]))
        else:
            X = np.arange(len(y)).reshape(-1, 1)
            model = LinearRegression()
            model.fit(X, y)
            prediction = float(
                model.predict(np.array([[len(y)]]))[0]
            )

        predicted_demand = max(
            0,
            round(float(prediction))
        )

        product_rows = data[
            data[product_col] == product
        ].sort_values(date_col)

        # Current stock
        current_stock = 0

        if stock_col:

            stock_values = product_rows[
                stock_col
            ].dropna()

            if not stock_values.empty:

                current_stock = max(
                    0,
                    float(stock_values.iloc[-1])
                )

        # Flexible lead time
        lead_time = default_lead_time

        if lead_col:

            lead_values = product_rows[
                lead_col
            ].dropna()

            if not lead_values.empty:

                lead_time = float(
                    lead_values.iloc[-1]
                )

        if not np.isfinite(lead_time) or lead_time <= 0:
            lead_time = default_lead_time

        lead_time = max(1, lead_time)

        # Demand calculations
        daily_demand = predicted_demand / 30

        # Initial safety stock assumption: 20%
        safety_stock = round(
            daily_demand * lead_time * 0.20
        )

        # Reorder Point
        reorder_point = round(
            daily_demand * lead_time + safety_stock
        )

        # Target stock for next 30 days
        target_stock = (
            predicted_demand + safety_stock
        )

        reorder_quantity = max(
            0,
            round(target_stock - current_stock)
        )

        # Inventory coverage and risk indicators.
        stock_coverage_days = (
            current_stock / daily_demand if daily_demand > 0 else float("inf")
        )

        if current_stock <= 0:
            status = "Out of Stock"
            risk_level = "Critical"
        elif current_stock <= reorder_point:
            status = "Reorder Required"
            risk_level = "High"
        elif stock_coverage_days <= lead_time + 3:
            status = "Low Stock"
            risk_level = "Medium"
        else:
            status = "Stock Available"
            risk_level = "Low"

        results.append({

            "Product": str(product),

            "Selected Model": selected_model,

            "Current Stock": round(current_stock),

            "Lead Time (Days)": round(lead_time),

            "Predicted Demand": predicted_demand,

            "Daily Demand": round(daily_demand, 2),

            "Stock Coverage (Days)": (
                round(stock_coverage_days, 1)
                if np.isfinite(stock_coverage_days) else "No demand"
            ),

            "Safety Stock": safety_stock,

            "Reorder Point": reorder_point,

            "Recommended Order": reorder_quantity,

            "Stock Status": status,

            "Inventory Risk": risk_level

        })

    return pd.DataFrame(results)


def evaluate_forecast_accuracy(df, detected):
    """Evaluate one-step-ahead monthly forecasts using a chronological holdout.

    For each product, train on all months except the latest month and predict
    that latest month. Products need at least four months of history.
    """
    product_col = detected["Product"]
    date_col = detected["Date"]
    sales_col = detected["Sales Quantity"]

    data = df[[product_col, date_col, sales_col]].copy()
    data[date_col] = pd.to_datetime(data[date_col], errors="coerce")
    data[sales_col] = pd.to_numeric(data[sales_col], errors="coerce")
    data = data.dropna(subset=[product_col, date_col, sales_col])
    data = data[data[sales_col] >= 0]

    if data.empty:
        return None, pd.DataFrame()

    data["Month"] = data[date_col].dt.to_period("M")
    monthly = (
        data.groupby([product_col, "Month"])[sales_col]
        .sum().reset_index()
    )

    rows = []
    for product in monthly[product_col].dropna().unique():
        product_data = monthly[monthly[product_col] == product].sort_values("Month").copy()
        # Need 3 training months plus 1 unseen test month.
        if len(product_data) < 4:
            continue

        product_data["Month_Number"] = np.arange(len(product_data))
        train = product_data.iloc[:-1]
        test = product_data.iloc[-1]

        model = LinearRegression()
        model.fit(train[["Month_Number"]], train[sales_col])
        predicted = max(0.0, float(model.predict(pd.DataFrame({"Month_Number": [test["Month_Number"]]}))[0]))
        actual = float(test[sales_col])

        rows.append({
            "Product": str(product),
            "Test Month": str(test["Month"]),
            "Actual Demand": round(actual, 2),
            "Predicted Demand": round(predicted, 2),
            "Absolute Error": round(abs(actual - predicted), 2),
            "Squared Error": (actual - predicted) ** 2,
        })

    if not rows:
        return None, pd.DataFrame()

    results = pd.DataFrame(rows)
    mae = float(results["Absolute Error"].mean())
    rmse = float(np.sqrt(results["Squared Error"].mean()))
    actual_total = float(results["Actual Demand"].sum())
    wape = (float(results["Absolute Error"].sum()) / actual_total * 100) if actual_total > 0 else None

    metrics = {"MAE": mae, "RMSE": rmse, "WAPE": wape, "Products Evaluated": len(results)}
    return metrics, results.drop(columns=["Squared Error"])


def compare_forecasting_models(df, detected):
    """Compare simple forecasting methods on the same latest-month holdout."""
    product_col = detected["Product"]
    date_col = detected["Date"]
    sales_col = detected["Sales Quantity"]

    data = df[[product_col, date_col, sales_col]].copy()
    data[date_col] = pd.to_datetime(data[date_col], errors="coerce")
    data[sales_col] = pd.to_numeric(data[sales_col], errors="coerce")
    data = data.dropna(subset=[product_col, date_col, sales_col])
    data = data[data[sales_col] >= 0]

    if data.empty:
        return pd.DataFrame(), pd.DataFrame(), None

    data["Month"] = data[date_col].dt.to_period("M")
    monthly = (
        data.groupby([product_col, "Month"])[sales_col]
        .sum()
        .reset_index()
    )

    rows = []
    for product in monthly[product_col].dropna().unique():
        product_data = (
            monthly[monthly[product_col] == product]
            .sort_values("Month")
            .reset_index(drop=True)
        )

        # Require 3 training months plus one unseen test month.
        if len(product_data) < 4:
            continue

        train = product_data.iloc[:-1].copy()
        test = product_data.iloc[-1]
        actual = float(test[sales_col])

        # 1) Naive: next month equals the latest observed month.
        naive_prediction = float(train[sales_col].iloc[-1])

        # 2) Moving average: mean of the latest 3 training months.
        moving_average_prediction = float(train[sales_col].tail(3).mean())

        # 3) Linear regression: fit a straight trend across training months.
        train_x = np.arange(len(train)).reshape(-1, 1)
        test_x = np.array([[len(train)]])
        linear_model = LinearRegression()
        linear_model.fit(train_x, train[sales_col].to_numpy())
        linear_prediction = float(linear_model.predict(test_x)[0])

        predictions = {
            "Naive": naive_prediction,
            "Moving Average (3 months)": moving_average_prediction,
            "Linear Regression": linear_prediction,
        }

        for model_name, prediction in predictions.items():
            prediction = max(0.0, prediction)
            rows.append({
                "Product": str(product),
                "Test Month": str(test["Month"]),
                "Model": model_name,
                "Actual Demand": actual,
                "Predicted Demand": prediction,
                "Absolute Error": abs(actual - prediction),
            })

    if not rows:
        return pd.DataFrame(), pd.DataFrame(), None

    details = pd.DataFrame(rows)
    summary_rows = []
    for model_name, group in details.groupby("Model", sort=False):
        actual_total = float(group["Actual Demand"].sum())
        absolute_error_total = float(group["Absolute Error"].sum())
        mae = float(group["Absolute Error"].mean())
        rmse = float(np.sqrt(np.mean(
            (group["Actual Demand"] - group["Predicted Demand"]) ** 2
        )))
        wape = (
            absolute_error_total / actual_total * 100
            if actual_total > 0 else None
        )
        summary_rows.append({
            "Model": model_name,
            "MAE (units)": mae,
            "RMSE (units)": rmse,
            "WAPE (%)": wape,
            "Products Evaluated": int(group["Product"].nunique()),
        })

    summary = pd.DataFrame(summary_rows).sort_values(
        "WAPE (%)", ascending=True, na_position="last"
    ).reset_index(drop=True)

    best_model = (
        str(summary.iloc[0]["Model"])
        if not summary.empty and pd.notna(summary.iloc[0]["WAPE (%)"])
        else None
    )
    summary["MAE (units)"] = summary["MAE (units)"].round(2)
    summary["RMSE (units)"] = summary["RMSE (units)"].round(2)
    summary["WAPE (%)"] = summary["WAPE (%)"].round(2)
    details["Actual Demand"] = details["Actual Demand"].round(2)
    details["Predicted Demand"] = details["Predicted Demand"].round(2)
    details["Absolute Error"] = details["Absolute Error"].round(2)

    return summary, details, best_model



# =====================================================
# 6. BUSINESS INSIGHTS GENERATION
# =====================================================

def generate_business_insights(df, detected, forecast):

    insights = []

    product_col = detected["Product"]
    date_col = detected["Date"]
    sales_col = detected["Sales Quantity"]

    data = df.copy()

    data[date_col] = pd.to_datetime(
        data[date_col],
        errors="coerce"
    )

    data[sales_col] = pd.to_numeric(
        data[sales_col],
        errors="coerce"
    )

    data = data.dropna(
        subset=[product_col, date_col, sales_col]
    )

    data = data[data[sales_col] >= 0]

    if data.empty:

        return ["No valid sales data available."]

    # Total units
    total_units = data[sales_col].sum()

    insights.append(
        f"Your business sold {total_units:,.0f} units "
        "in the uploaded data."
    )

    # Product performance
    product_sales = (
        data.groupby(product_col)[sales_col]
        .sum()
        .sort_values(ascending=False)
    )

    best_product = product_sales.index[0]

    insights.append(
        f"{best_product} is your best-selling product "
        f"with {product_sales.iloc[0]:,.0f} units sold."
    )

    if len(product_sales) > 1:

        slow_product = product_sales.index[-1]

        insights.append(
            f"{slow_product} has the lowest sales "
            "among the analyzed products. Review demand "
            "before placing large orders."
        )

    # Revenue
    price_col = detected.get("Unit Price")

    if price_col:

        data[price_col] = pd.to_numeric(
            data[price_col],
            errors="coerce"
        )

        revenue = (
            data[sales_col] * data[price_col]
        ).sum()

        insights.append(
            f"Estimated revenue is Rs. {revenue:,.2f}."
        )

    # Monthly sales trend
    data["Month"] = data[date_col].dt.to_period("M")

    monthly = (
        data.groupby("Month")[sales_col]
        .sum()
        .sort_index()
    )

    if len(monthly) >= 2:

        first = monthly.iloc[0]
        last = monthly.iloc[-1]

        if last > first:

            insights.append(
                "Sales increased between the first and "
                "last months in the uploaded data."
            )

        elif last < first:

            insights.append(
                "Sales decreased between the first and "
                "last months. Review demand before "
                "increasing inventory."
            )

        else:

            insights.append(
                "Sales remained at the same level between "
                "the first and last months."
            )

    # Forecast recommendations
    if not forecast.empty:

        reorder_products = forecast[
            forecast["Stock Status"] == "Reorder Required"
        ]

        if not reorder_products.empty:

            names = ", ".join(
                reorder_products["Product"].astype(str)
            )

            insights.append(
                f"Reordering is recommended for: {names}."
            )

        else:

            insights.append(
                "No products are currently below "
                "their calculated reorder point."
            )

        highest = forecast.loc[
            forecast["Predicted Demand"].idxmax()
        ]

        insights.append(
            f"{highest['Product']} has the highest "
            "predicted demand among the analyzed products."
        )

    return insights


# =====================================================
# 7. PDF REPORT GENERATION
# =====================================================

def generate_pdf_report(
    forecast,
    insights,
    total_units,
    total_revenue=None,
    total_profit=None
):

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm
    )

    styles = getSampleStyleSheet()

    elements = []

    # Report title
    elements.append(
        Paragraph(
            "AI Inventory Intelligence Report",
            styles["Title"]
        )
    )

    elements.append(Spacer(1, 10))

    elements.append(
        Paragraph(
            f"Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M')}",
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 18))

    # Business summary
    elements.append(
        Paragraph(
            "Business Performance Summary",
            styles["Heading2"]
        )
    )

    summary = [
        ["Metric", "Value"],
        ["Total Units Sold", f"{total_units:,.0f}"],
        [
            "Estimated Revenue",
            f"Rs. {total_revenue:,.2f}"
            if total_revenue is not None
            else "Unavailable"
        ],
        [
            "Estimated Gross Profit",
            f"Rs. {total_profit:,.2f}"
            if total_profit is not None
            else "Unavailable"
        ]
    ]

    summary_table = Table(
        summary,
        colWidths=[85 * mm, 80 * mm]
    )

    summary_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("PADDING", (0, 0), (-1, -1), 7),
        ])
    )

    elements.append(summary_table)

    elements.append(Spacer(1, 20))

    # Forecast section
    elements.append(
        Paragraph(
            "Demand Forecast and Replenishment",
            styles["Heading2"]
        )
    )

    forecast_data = [
        [
            "Product",
            "Demand",
            "Stock",
            "Reorder",
            "Lead Days"
        ]
    ]

    for _, row in forecast.iterrows():

        forecast_data.append([
            str(row["Product"]),
            str(row["Predicted Demand"]),
            str(row["Current Stock"]),
            str(row["Recommended Order"]),
            str(row["Lead Time (Days)"])
        ])

    forecast_table = Table(
        forecast_data,
        repeatRows=1,
        colWidths=[
            42 * mm,
            27 * mm,
            27 * mm,
            30 * mm,
            28 * mm
        ]
    )

    forecast_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("PADDING", (0, 0), (-1, -1), 6),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ])
    )

    elements.append(forecast_table)

    elements.append(Spacer(1, 20))

    # Insights section
    elements.append(
        Paragraph(
            "Business Insights and Recommendations",
            styles["Heading2"]
        )
    )

    for number, insight in enumerate(insights, start=1):

        safe_insight = (
            str(insight)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

        elements.append(
            Paragraph(
                f"{number}. {safe_insight}",
                styles["BodyText"]
            )
        )

        elements.append(Spacer(1, 8))

    document.build(elements)

    buffer.seek(0)

    return buffer.getvalue()


# =====================================================
# 8. MYSQL DATABASE OPERATIONS
# =====================================================

def save_analysis_to_mysql(file_name, df, detected, forecast, default_lead_time):
    """Save one uploaded file, its sales rows, latest inventory and forecasts.

    Each successful analysis creates a new uploads record. This preserves
    upload history and avoids silently mixing rows from different files.
    """
    connection = get_connection()
    if connection is None:
        raise RuntimeError("Could not connect to MySQL. Check config/database.py and .env.")

    cursor = connection.cursor()
    try:
        product_col = detected["Product"]
        date_col = detected["Date"]
        sales_col = detected["Sales Quantity"]
        category_col = detected.get("Category")
        stock_col = detected.get("Current Stock")
        price_col = detected.get("Unit Price")
        cost_col = detected.get("Unit Cost")
        lead_col = detected.get("Lead Time")

        data = df.copy()
        data[date_col] = pd.to_datetime(data[date_col], errors="coerce")
        data[sales_col] = pd.to_numeric(data[sales_col], errors="coerce")
        data = data.dropna(subset=[product_col, date_col, sales_col])
        data = data[data[sales_col] >= 0].copy()
        if data.empty:
            raise ValueError("No valid product/date/sales rows were found to save.")

        # Convert optional numeric columns safely.
        for col in [stock_col, price_col, cost_col, lead_col]:
            if col:
                data[col] = pd.to_numeric(data[col], errors="coerce")

        cursor.execute(
            "INSERT INTO uploads (file_name, total_rows, status) VALUES (%s, %s, %s)",
            (str(file_name)[:255], int(len(data)), "Saved")
        )
        upload_id = cursor.lastrowid

        # Save/update each product once, then link its sales and inventory.
        product_ids = {}
        for product_name in data[product_col].dropna().unique():
            name = str(product_name).strip()
            if not name:
                continue
            product_rows = data[data[product_col].astype(str).str.strip() == name]
            latest_row = product_rows.sort_values(date_col).iloc[-1]

            category = None
            if category_col and pd.notna(latest_row[category_col]):
                category = str(latest_row[category_col])[:100]
            unit_price = None
            if price_col and pd.notna(latest_row[price_col]):
                unit_price = float(latest_row[price_col])
            unit_cost = None
            if cost_col and pd.notna(latest_row[cost_col]):
                unit_cost = float(latest_row[cost_col])

            cursor.execute(
                "SELECT product_id FROM products WHERE product_name = %s ORDER BY product_id LIMIT 1",
                (name[:150],)
            )
            found = cursor.fetchone()
            if found:
                product_id = found[0]
                cursor.execute(
                    "UPDATE products SET category=%s, unit_price=%s, unit_cost=%s WHERE product_id=%s",
                    (category, unit_price, unit_cost, product_id)
                )
            else:
                cursor.execute(
                    "INSERT INTO products (product_name, category, unit_price, unit_cost) VALUES (%s, %s, %s, %s)",
                    (name[:150], category, unit_price, unit_cost)
                )
                product_id = cursor.lastrowid
            product_ids[name] = product_id

            # Current inventory is taken from the latest dated row for this product.
            current_stock = 0
            if stock_col:
                stock_values = product_rows[stock_col].dropna()
                if not stock_values.empty:
                    current_stock = max(0, int(round(float(stock_values.iloc[-1]))))

            lead_time = int(default_lead_time)
            if lead_col:
                lead_values = product_rows[lead_col].dropna()
                lead_values = lead_values[lead_values > 0]
                if not lead_values.empty:
                    lead_time = max(1, int(round(float(lead_values.iloc[-1]))))

            cursor.execute(
                "INSERT INTO inventory (product_id, current_stock, lead_time_days) "
                "VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE "
                "current_stock=VALUES(current_stock), lead_time_days=VALUES(lead_time_days)",
                (product_id, current_stock, lead_time)
            )

        # Save every valid sales row and associate it with this upload.
        for _, row in data.iterrows():
            name = str(row[product_col]).strip()
            product_id = product_ids.get(name)
            if product_id is None:
                continue
            units = int(round(float(row[sales_col])))
            revenue = None
            if price_col and pd.notna(row[price_col]):
                revenue = float(row[sales_col]) * float(row[price_col])
            sale_date = pd.Timestamp(row[date_col]).date()
            cursor.execute(
                "INSERT INTO sales (product_id, sale_date, units_sold, revenue, upload_id) "
                "VALUES (%s, %s, %s, %s, %s)",
                (product_id, sale_date, units, revenue, upload_id)
            )

        # Forecast is for the month immediately after the latest uploaded date.
        latest_date = data[date_col].max()
        next_month_date = (latest_date + pd.offsets.MonthBegin(1)).date()
        for _, row in forecast.iterrows():
            product_id = product_ids.get(str(row["Product"]).strip())
            if product_id is None:
                continue
            cursor.execute(
                "INSERT INTO forecasts (product_id, forecast_date, predicted_demand, model_name, upload_id) "
                "VALUES (%s, %s, %s, %s, %s)",
                (product_id, next_month_date, float(row["Predicted Demand"]), "LinearRegression", upload_id)
            )

        connection.commit()
        return upload_id, len(data), len(forecast)

    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


def load_forecast_history(limit=100):
    """Fetch recent saved forecast records with product and upload details."""
    connection = get_connection()
    if connection is None:
        raise RuntimeError("Could not connect to MySQL.")
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT f.forecast_id, p.product_name, f.forecast_date, "
            "f.predicted_demand, f.model_name, f.created_at, u.file_name, f.upload_id "
            "FROM forecasts f JOIN products p ON f.product_id=p.product_id "
            "LEFT JOIN uploads u ON f.upload_id=u.upload_id "
            "ORDER BY f.created_at DESC, f.forecast_id DESC LIMIT %s",
            (int(limit),)
        )
        return pd.DataFrame(cursor.fetchall())
    finally:
        cursor.close()
        connection.close()


# =====================================================
# 9. FILE UPLOAD
# =====================================================

st.markdown('<div id="upload-data"></div>', unsafe_allow_html=True)
st.header("Upload your business data")
st.markdown('<div class="section-intro">Start with your existing sales or inventory spreadsheet. We will inspect the columns before running the forecast.</div>', unsafe_allow_html=True)
with st.container(border=True):
    uploaded_file = st.file_uploader(
        "Choose a CSV or Excel file",
        type=["csv", "xlsx", "xls"],
        help="Supported formats: .csv, .xlsx and .xls. Required information: product name, transaction date and quantity sold."
    )
    st.caption("Tip: Your file can use common alternative column names. The app will try to detect them automatically.")


if uploaded_file is not None:

    try:

        # Read uploaded file
        if uploaded_file.name.lower().endswith(".csv"):

            df = pd.read_csv(uploaded_file)

        else:

            df = pd.read_excel(uploaded_file)

        if df.empty:

            st.error("Uploaded file is empty.")
            st.stop()

        st.success("File uploaded successfully!")

        # =================================================
        # 9. DATA OVERVIEW
        # =================================================

        st.header("1. Your data at a glance")

        c1, c2, c3 = st.columns(3)

        c1.metric("Total Rows", len(df))

        c2.metric("Total Columns", len(df.columns))

        c3.metric(
            "Missing Values",
            int(df.isnull().sum().sum())
        )

        st.subheader("Uploaded Data Preview")

        st.dataframe(
            df.head(20),
            use_container_width=True
        )

        # =================================================
        # 10. AUTOMATIC COLUMN DETECTION
        # =================================================

        st.header("2. Column matching")

        detected = detect_columns(df)

        for role in COLUMN_ALIASES:

            if role in detected:

                st.success(
                    f"{role} → {detected[role]}"
                )

            else:

                st.warning(
                    f"{role} → Not detected"
                )

        # =================================================
        # 11. DATA QUALITY
        # =================================================

        st.header("3. Data quality check")

        quality = pd.DataFrame({

            "Column": df.columns,

            "Data Type": df.dtypes.astype(str).values,

            "Missing Values": df.isnull().sum().values,

            "Unique Values": df.nunique().values

        })

        st.dataframe(
            quality,
            use_container_width=True
        )

        # =================================================
        # 12. REQUIRED COLUMN VALIDATION
        # =================================================

        required = [
            "Product",
            "Date",
            "Sales Quantity"
        ]

        missing = [
            col for col in required
            if col not in detected
        ]

        if missing:

            st.error(
                "Required columns missing: "
                + ", ".join(missing)
            )

            st.stop()

        # =================================================
        # 13. LEAD TIME SETTINGS
        # =================================================

        st.header("4. Supplier delivery settings")

        if "Lead Time" in detected:

            st.success(
                "Lead Time column detected. "
                "Uploaded product-wise values will be used "
                "where available."
            )

        else:

            st.info(
                "Lead Time column not detected. "
                "Default supplier delivery time will be used."
            )

        default_lead_time = st.number_input(
            "Default Supplier Delivery Time (Days)",
            min_value=1,
            max_value=90,
            value=7
        )

        # =================================================
        # 14. FORECAST BUTTON
        # =================================================

        st.markdown('<div id="demand-forecast"></div>', unsafe_allow_html=True)
        st.header("5. Generate your demand forecast")

        if st.button(
            "✨ Generate demand forecast",
            type="primary"
        ):

            # Choose the lowest-error model separately for each product.
            _comparison_summary, _comparison_details, _overall_best_model = (
                compare_forecasting_models(df, detected)
            )

            selected_models = {}
            if not _comparison_details.empty:
                for product_name, product_results in _comparison_details.groupby("Product"):
                    best_row = product_results.sort_values(
                        ["Absolute Error", "Model"]
                    ).iloc[0]
                    selected_models[str(product_name)] = str(best_row["Model"])

            forecast = forecast_demand(
                df,
                detected,
                default_lead_time,
                selected_models
            )

            if not forecast.empty:
                st.info(
                    "Automatic model selection is performed separately for each product. "
                    "Products without enough validation history use Linear Regression as the fallback."
                )
                st.dataframe(
                    forecast[["Product", "Selected Model"]],
                    use_container_width=True,
                    hide_index=True
                )

            if forecast.empty:

                st.warning(
                    "Not enough valid historical data. "
                    "Each product requires at least "
                    "3 months of sales history."
                )

                st.stop()


            # =================================================
            # ADVANCED INVENTORY INTELLIGENCE
            # =================================================
            st.header("6. Advanced inventory intelligence")
            st.caption(
                "Stock alerts and order suggestions are calculated from forecast demand, "
                "current stock and supplier lead time. Review quantities with your supplier "
                "before placing a purchase order."
            )

            out_of_stock = forecast[forecast["Stock Status"] == "Out of Stock"]
            reorder_alerts = forecast[forecast["Stock Status"] == "Reorder Required"]
            low_stock_alerts = forecast[forecast["Stock Status"] == "Low Stock"]
            total_recommended_units = int(forecast["Recommended Order"].sum())
            critical_count = int((forecast["Inventory Risk"] == "Critical").sum())
            high_count = int((forecast["Inventory Risk"] == "High").sum())
            medium_count = int((forecast["Inventory Risk"] == "Medium").sum())

            inv1, inv2, inv3, inv4 = st.columns(4)
            inv1.metric("Out of stock", len(out_of_stock))
            inv2.metric("Reorder required", len(reorder_alerts))
            inv3.metric("Low stock", len(low_stock_alerts))
            inv4.metric("Suggested order units", total_recommended_units)

            if not out_of_stock.empty:
                st.error(
                    "Out-of-stock products: "
                    + ", ".join(out_of_stock["Product"].astype(str).tolist())
                )
            if not reorder_alerts.empty:
                st.warning(
                    "Reorder point reached: "
                    + ", ".join(reorder_alerts["Product"].astype(str).tolist())
                )
            if not low_stock_alerts.empty:
                st.info(
                    "Low stock coverage: "
                    + ", ".join(low_stock_alerts["Product"].astype(str).tolist())
                )
            if out_of_stock.empty and reorder_alerts.empty and low_stock_alerts.empty:
                st.success("No immediate stock alerts based on the current assumptions.")

            st.subheader("Inventory risk overview")
            risk_counts = (
                forecast["Inventory Risk"]
                .value_counts()
                .reindex(["Critical", "High", "Medium", "Low"], fill_value=0)
            )
            risk_left, risk_right = st.columns([1, 2])
            with risk_left:
                st.dataframe(
                    risk_counts.rename_axis("Risk Level").reset_index(name="Products"),
                    use_container_width=True,
                    hide_index=True
                )
            with risk_right:
                st.bar_chart(risk_counts)

            st.subheader("Reorder recommendations")
            reorder_view = forecast[
                forecast["Recommended Order"] > 0
            ][[
                "Product", "Current Stock", "Predicted Demand",
                "Lead Time (Days)", "Reorder Point", "Recommended Order",
                "Stock Coverage (Days)", "Inventory Risk"
            ]].sort_values(
                ["Inventory Risk", "Recommended Order"],
                ascending=[True, False]
            )

            if reorder_view.empty:
                st.success("No purchase quantity is recommended for the current forecast.")
            else:
                st.dataframe(reorder_view, use_container_width=True, hide_index=True)
                csv_bytes = reorder_view.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "Download reorder recommendations (CSV)",
                    data=csv_bytes,
                    file_name="inventory_reorder_recommendations.csv",
                    mime="text/csv"
                )

            with st.expander("View complete inventory intelligence table", expanded=False):
                st.dataframe(forecast, use_container_width=True, hide_index=True)

            # =================================================
            # FORECAST ACCURACY EVALUATION
            # =================================================
            st.subheader("Forecast accuracy evaluation")
            st.caption(
                "This is a historical holdout test: the model trains on earlier months "
                "and predicts the latest unseen month. Lower MAE, RMSE and WAPE indicate "
                "smaller forecast errors. This is an estimate, not a guarantee of future accuracy."
            )

            accuracy_metrics, accuracy_details = evaluate_forecast_accuracy(df, detected)
            if accuracy_metrics is None:
                st.info(
                    "Accuracy metrics need at least 4 months of valid sales history per product "
                    "(3 training months plus 1 test month). Upload a longer history to evaluate accuracy."
                )
            else:
                a1, a2, a3, a4 = st.columns(4)
                a1.metric("MAE", f"{accuracy_metrics['MAE']:.2f} units")
                a2.metric("RMSE", f"{accuracy_metrics['RMSE']:.2f} units")
                a3.metric(
                    "WAPE",
                    f"{accuracy_metrics['WAPE']:.1f}%" if accuracy_metrics["WAPE"] is not None else "N/A"
                )
                a4.metric("Products evaluated", accuracy_metrics["Products Evaluated"])
                with st.expander("View accuracy test details", expanded=False):
                    st.dataframe(accuracy_details, use_container_width=True, hide_index=True)


            # =================================================
            # FORECAST MODEL COMPARISON
            # =================================================
            st.subheader("Forecast model comparison")
            st.caption(
                "All three methods are tested against the same latest unseen month for each product. "
                "The model with the lowest WAPE has the smallest total percentage error on this test."
            )

            comparison_summary, comparison_details, best_model = compare_forecasting_models(
                df, detected
            )

            if comparison_summary.empty:
                st.info(
                    "Model comparison needs at least 4 months of valid sales history per product. "
                    "Upload more historical data and try again."
                )
            else:
                if best_model:
                    st.success(f"Best-performing model on this test: {best_model}")
                st.dataframe(
                    comparison_summary,
                    use_container_width=True,
                    hide_index=True
                )
                st.bar_chart(
                    comparison_summary.set_index("Model")[["WAPE (%)"]]
                )
                with st.expander("View product-wise model predictions", expanded=False):
                    st.dataframe(
                        comparison_details.sort_values(["Product", "Model"]),
                        use_container_width=True,
                        hide_index=True
                    )
                st.caption(
                    "Important: this is a small historical holdout comparison, not proof that one model "
                    "will always be best. Re-test with more months and real business data before deployment."
                )

            # Save uploaded data and forecast to MySQL as one transaction.
            try:
                saved_upload_id, saved_sales_rows, saved_forecast_rows = save_analysis_to_mysql(
                    uploaded_file.name,
                    df,
                    detected,
                    forecast,
                    default_lead_time
                )
                st.success(
                    f"Forecast completed and saved to MySQL! Upload ID: {saved_upload_id} | "
                    f"Sales rows saved: {saved_sales_rows} | Forecast rows saved: {saved_forecast_rows}"
                )
            except Exception as db_error:
                st.error(f"Forecast generated, but MySQL saving failed: {db_error}")
                st.info("Check your MySQL connection and table structure. Your forecast is still available below.")

            # =================================================
            # 15. BUSINESS ANALYTICS
            # =================================================

            st.header("7. Business performance")

            analytics = df.copy()

            analytics[detected["Date"]] = pd.to_datetime(
                analytics[detected["Date"]],
                errors="coerce"
            )

            analytics[detected["Sales Quantity"]] = pd.to_numeric(
                analytics[detected["Sales Quantity"]],
                errors="coerce"
            )

            analytics = analytics.dropna(
                subset=[
                    detected["Date"],
                    detected["Sales Quantity"],
                    detected["Product"]
                ]
            )

            analytics = analytics[
                analytics[detected["Sales Quantity"]] >= 0
            ]

            sales_col = detected["Sales Quantity"]
            product_col = detected["Product"]

            total_units = analytics[sales_col].sum()

            # Revenue
            total_revenue = None

            price_col = detected.get("Unit Price")

            if price_col:

                analytics[price_col] = pd.to_numeric(
                    analytics[price_col],
                    errors="coerce"
                )

                total_revenue = (
                    analytics[sales_col] *
                    analytics[price_col]
                ).sum()

            # Gross profit
            total_profit = None

            cost_col = detected.get("Unit Cost")

            if price_col and cost_col:

                analytics[cost_col] = pd.to_numeric(
                    analytics[cost_col],
                    errors="coerce"
                )

                total_profit = (
                    analytics[sales_col] *
                    (
                        analytics[price_col] -
                        analytics[cost_col]
                    )
                ).sum()

            # KPI cards
            k1, k2, k3 = st.columns(3)

            k1.metric(
                "Total Units Sold",
                f"{total_units:,.0f}"
            )

            k2.metric(
                "Estimated Revenue",
                f"Rs. {total_revenue:,.2f}"
                if total_revenue is not None
                else "Unavailable"
            )

            k3.metric(
                "Estimated Gross Profit",
                f"Rs. {total_profit:,.2f}"
                if total_profit is not None
                else "Unavailable"
            )

            # Monthly sales chart
            st.subheader("Monthly Sales Trend")

            analytics["Month"] = (
                analytics[detected["Date"]]
                .dt.to_period("M")
                .astype(str)
            )

            monthly_sales = (
                analytics.groupby("Month")[sales_col]
                .sum()
                .reset_index()
            )

            st.line_chart(
                monthly_sales.set_index("Month")
            )

            # Product performance chart
            st.subheader("Product-wise Sales Performance")

            product_sales = (
                analytics.groupby(product_col)[sales_col]
                .sum()
                .sort_values(ascending=False)
            )

            st.bar_chart(product_sales)

            # Revenue chart
            if price_col:

                st.subheader("Product-wise Revenue")

                analytics["Revenue"] = (
                    analytics[sales_col] *
                    analytics[price_col]
                )

                revenue_by_product = (
                    analytics.groupby(product_col)["Revenue"]
                    .sum()
                    .sort_values(ascending=False)
                )

                st.bar_chart(revenue_by_product)

            # =================================================
            # 16. FORECAST RESULTS
            # =================================================

            st.markdown('<div id="inventory-results"></div>', unsafe_allow_html=True)
            st.header("7. Forecast results")

            st.dataframe(
                forecast,
                use_container_width=True
            )

            st.subheader("Predicted Product Demand")

            st.bar_chart(
                forecast.set_index("Product")[
                    ["Predicted Demand"]
                ]
            )

            # =================================================
            # 17. REPLENISHMENT ALERTS
            # =================================================

            st.header("8. Stock recommendations")

            for _, row in forecast.iterrows():

                st.write(f"**{row['Product']}**")

                if row["Stock Status"] == "Reorder Required":

                    st.warning(
                        f"Reorder {row['Recommended Order']} units. "
                        f"Current stock: {row['Current Stock']}, "
                        f"Reorder point: {row['Reorder Point']}."
                    )

                else:

                    st.success(
                        f"Stock available. Current stock: "
                        f"{row['Current Stock']} units."
                    )

            # =================================================
            # 18. BUSINESS INSIGHTS
            # =================================================

            st.header("9. Business insights")
            st.caption("Automatically generated recommendations based on the uploaded data and forecast results.")

            insights = generate_business_insights(
                df,
                detected,
                forecast
            )

            for number, insight in enumerate(
                insights,
                start=1
            ):

                st.info(
                    f"{number}. {insight}"
                )

            # =================================================
            # 19. CSV DOWNLOAD
            # =================================================

            st.header("10. Export your reports")

            csv_data = forecast.to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                label="Download Forecast CSV",
                data=csv_data,
                file_name="inventory_forecast_report.csv",
                mime="text/csv"
            )

            # =================================================
            # 20. PDF DOWNLOAD
            # =================================================

            pdf_data = generate_pdf_report(
                forecast,
                insights,
                total_units,
                total_revenue,
                total_profit
            )

            st.download_button(
                label="Download Business Report (PDF)",
                data=pdf_data,
                file_name="AI_Inventory_Business_Report.pdf",
                mime="application/pdf"
            )

    except Exception as error:

        st.error(
            f"Something went wrong: {error}"
        )

else:

    st.info(
        "Your workspace is ready. Upload a CSV or Excel file above to begin. "
        "The file should include product, date and sales quantity columns."
    )


# =====================================================
# 21. SAVED FORECAST HISTORY
# =====================================================

st.divider()
st.markdown('<div id="forecast-history"></div>', unsafe_allow_html=True)
st.header("Saved forecast history")
st.markdown('<div class="section-intro">Review previous forecasts saved in your MySQL database.</div>', unsafe_allow_html=True)
if st.button("Refresh Forecast History"):
    try:
        history = load_forecast_history()
        if history.empty:
            st.info("No saved forecasts found yet. Upload a file and predict demand first.")
        else:
            st.dataframe(history, use_container_width=True)
    except Exception as history_error:
        st.error(f"Could not load forecast history: {history_error}")


# =====================================================
# 22. FREE LOCAL INVENTORY CHATBOT (NO API REQUIRED)
# =====================================================

def answer_inventory_question(question):
    """Answer supported inventory questions using safe, fixed MySQL queries.

    This is a local rule-based chatbot, not a generative AI model. It reads
    the most recently uploaded dataset so separate uploads are not mixed.
    """
    q = str(question).strip().lower()
    if not q:
        return "Please type a question about your inventory or sales."

    connection = get_connection()
    if connection is None:
        return "I could not connect to MySQL. Please check config/database.py and your .env settings."

    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT MAX(upload_id) AS latest_upload_id FROM uploads WHERE status = 'Saved'")
        upload_row = cursor.fetchone() or {}
        latest_upload_id = upload_row.get("latest_upload_id")
        if latest_upload_id is None:
            return "No uploaded business data is saved yet. Upload a CSV/Excel file and run demand forecasting first."

        # Highest / best-selling product in the latest upload.
        if any(term in q for term in ["best selling", "best-selling", "highest sales", "most sold", "top selling", "highest demand"]):
            cursor.execute(
                "SELECT p.product_name, SUM(s.units_sold) AS units "
                "FROM sales s JOIN products p ON p.product_id=s.product_id "
                "WHERE s.upload_id=%s GROUP BY p.product_id, p.product_name "
                "ORDER BY units DESC LIMIT 1", (latest_upload_id,)
            )
            row = cursor.fetchone()
            if row:
                return f"{row['product_name']} is the best-selling product in the latest uploaded file, with {row['units']:,.0f} units sold."
            return "I couldn't find sales records in the latest upload."

        # Lowest-selling product.
        if any(term in q for term in ["lowest sales", "least sold", "slow moving", "slow-moving", "worst selling"]):
            cursor.execute(
                "SELECT p.product_name, SUM(s.units_sold) AS units "
                "FROM sales s JOIN products p ON p.product_id=s.product_id "
                "WHERE s.upload_id=%s GROUP BY p.product_id, p.product_name "
                "ORDER BY units ASC LIMIT 1", (latest_upload_id,)
            )
            row = cursor.fetchone()
            if row:
                return f"{row['product_name']} has the lowest sales in the latest uploaded file, with {row['units']:,.0f} units sold. Consider reviewing its demand before placing a large order."
            return "I couldn't find sales records in the latest upload."

        # Revenue.
        if any(term in q for term in ["revenue", "sales value", "turnover", "income"]):
            cursor.execute(
                "SELECT SUM(revenue) AS revenue FROM sales WHERE upload_id=%s", (latest_upload_id,)
            )
            value = (cursor.fetchone() or {}).get("revenue")
            if value is None:
                return "Revenue is unavailable because unit prices were not provided in the uploaded data."
            return f"Estimated revenue in the latest uploaded file is Rs. {float(value):,.2f}. This is calculated from units sold multiplied by unit price."

        # Total units.
        if any(term in q for term in ["total units", "units sold", "total sales", "how many sold", "quantity sold"]):
            cursor.execute("SELECT COALESCE(SUM(units_sold),0) AS units FROM sales WHERE upload_id=%s", (latest_upload_id,))
            units = (cursor.fetchone() or {}).get("units", 0)
            return f"The latest uploaded file contains {float(units):,.0f} units sold."

        # Forecast / expected demand.
        if any(term in q for term in ["forecast", "predicted demand", "expected demand", "next month", "future demand"]):
            cursor.execute(
                "SELECT p.product_name, f.predicted_demand, f.forecast_date "
                "FROM forecasts f JOIN products p ON p.product_id=f.product_id "
                "WHERE f.upload_id=%s ORDER BY f.predicted_demand DESC", (latest_upload_id,)
            )
            rows = cursor.fetchall()
            if not rows:
                return "No forecast is saved for the latest upload yet. Run Predict Future Demand first."
            lines = [f"{r['product_name']}: {float(r['predicted_demand']):,.0f} units (forecast date: {r['forecast_date']})" for r in rows]
            return "Saved demand forecast for the latest upload:\n" + "\n".join(lines)

        # Inventory / current stock list.
        if any(term in q for term in ["current stock", "available stock", "inventory level", "stock available", "show stock", "stock list"]):
            cursor.execute(
                "SELECT p.product_name, i.current_stock, i.lead_time_days "
                "FROM inventory i JOIN products p ON p.product_id=i.product_id "
                "WHERE EXISTS (SELECT 1 FROM sales s WHERE s.product_id=p.product_id AND s.upload_id=%s) "
                "ORDER BY p.product_name", (latest_upload_id,)
            )
            rows = cursor.fetchall()
            if not rows:
                return "No inventory records were found for the latest upload."
            return "Current inventory recorded for the latest upload:\n" + "\n".join(
                f"{r['product_name']}: {int(r['current_stock'])} units in stock; supplier lead time: {r['lead_time_days']} days"
                for r in rows
            )

        # Low stock / restock: compare available stock with saved predicted demand.
        if any(term in q for term in ["restock", "reorder", "low stock", "need to order", "shortage"]):
            cursor.execute(
                "SELECT p.product_name, i.current_stock, f.predicted_demand "
                "FROM forecasts f JOIN products p ON p.product_id=f.product_id "
                "JOIN inventory i ON i.product_id=p.product_id "
                "WHERE f.upload_id=%s ORDER BY p.product_name", (latest_upload_id,)
            )
            rows = cursor.fetchall()
            if not rows:
                return "No saved forecasts are available. Run Predict Future Demand first."
            low = [r for r in rows if float(r['current_stock']) < float(r['predicted_demand'])]
            if not low:
                return "Based on a simple comparison of current stock against predicted next-period demand, no product is below its forecast demand. This is not a full reorder-point calculation."
            return "These products have current stock below their predicted demand:\n" + "\n".join(
                f"{r['product_name']}: stock {int(r['current_stock'])}, predicted demand {float(r['predicted_demand']):,.0f}. Review replenishment."
                for r in low
            ) + "\nNote: this quick check compares stock with forecast demand; use the dashboard's reorder-point calculation for the full recommendation."

        # Product list.
        if any(term in q for term in ["list products", "all products", "which products", "product names"]):
            cursor.execute(
                "SELECT DISTINCT p.product_name FROM products p "
                "JOIN sales s ON s.product_id=p.product_id WHERE s.upload_id=%s "
                "ORDER BY p.product_name", (latest_upload_id,)
            )
            names = [r['product_name'] for r in cursor.fetchall()]
            return "Products in the latest uploaded file: " + (", ".join(names) if names else "No products found.")

        return (
            "I can answer these types of questions from your saved MySQL data:\n"
            "• Which product has the highest or lowest sales?\n"
            "• What is my estimated revenue?\n"
            "• How many total units were sold?\n"
            "• Show predicted demand / next month's forecast.\n"
            "• Show current stock.\n"
            "• Which products may need restocking?\n"
            "• List all products.\n\n"
            "Try asking one of these in simple English."
        )
    except Exception as error:
        return f"I couldn't process that question because of a database error: {error}"
    finally:
        cursor.close()
        connection.close()


st.divider()
st.markdown('<div id="business-assistant"></div>', unsafe_allow_html=True)
st.header("Ask your inventory assistant")
st.markdown('<div class="section-intro">Ask simple questions about sales, stock levels, revenue and saved forecasts.</div>', unsafe_allow_html=True)
st.caption("Free local chatbot: answers supported questions using your latest saved MySQL upload. No OpenAI API key or API credits required.")

if "inventory_chat_messages" not in st.session_state:
    st.session_state.inventory_chat_messages = [
        {"role": "assistant", "content": "Hello! I can answer questions about your latest saved inventory upload. Try: Which product has the highest sales?"}
    ]

for chat_message in st.session_state.inventory_chat_messages:
    with st.chat_message(chat_message["role"]):
        st.markdown(chat_message["content"])

user_question = st.chat_input("Ask about sales, stock, revenue or demand forecast...")
if user_question:
    st.session_state.inventory_chat_messages.append({"role": "user", "content": user_question})
    with st.chat_message("user"):
        st.markdown(user_question)
    bot_answer = answer_inventory_question(user_question)
    st.session_state.inventory_chat_messages.append({"role": "assistant", "content": bot_answer})
    with st.chat_message("assistant"):
        st.markdown(bot_answer)

if st.button("Clear chatbot conversation"):
    st.session_state.inventory_chat_messages = []
    st.rerun()
