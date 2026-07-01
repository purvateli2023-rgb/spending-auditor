import streamlit as st
import pandas as pd
import plotly.express as px
import pytesseract
from PIL import Image
import fitz
import io
import re
from transformers import pipeline

pytesseract.pytesseract.tesseract_cmd = r"C:\Users\pur03\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"

st.set_page_config(page_title="AI Spending Auditor", layout="wide")
st.title("💰 AI Spending Auditor")

categories = [
    "Groceries and Supermarkets",
    "Streaming and Subscriptions",
    "Dining and Restaurants and Food Delivery",
    "Transport and Fuel and Gas Station",
    "Entertainment and Gaming",
    "Utilities and Bills and Electricity and Water",
    "Shopping and Clothing and Fashion",
    "Health and Pharmacy and Medical",
    "Other"
]

KEYWORD_MAP = {
    "netflix": "Streaming and Subscriptions",
    "spotify": "Streaming and Subscriptions",
    "amazon prime": "Streaming and Subscriptions",
    "hulu": "Streaming and Subscriptions",
    "disney": "Streaming and Subscriptions",
    "walmart": "Groceries and Supermarkets",
    "costco": "Groceries and Supermarkets",
    "whole foods": "Groceries and Supermarkets",
    "trader joe": "Groceries and Supermarkets",
    "kroger": "Groceries and Supermarkets",
    "uber": "Transport and Fuel and Gas Station",
    "lyft": "Transport and Fuel and Gas Station",
    "shell": "Transport and Fuel and Gas Station",
    "gas": "Transport and Fuel and Gas Station",
    "mcdonald": "Dining and Restaurants and Food Delivery",
    "starbucks": "Dining and Restaurants and Food Delivery",
    "domino": "Dining and Restaurants and Food Delivery",
    "chipotle": "Dining and Restaurants and Food Delivery",
    "pizza": "Dining and Restaurants and Food Delivery",
    "electricity": "Utilities and Bills and Electricity and Water",
    "water bill": "Utilities and Bills and Electricity and Water",
    "cvs": "Health and Pharmacy and Medical",
    "pharmacy": "Health and Pharmacy and Medical",
    "zara": "Shopping and Clothing and Fashion",
    "nike": "Shopping and Clothing and Fashion",
    "adidas": "Shopping and Clothing and Fashion",
}

@st.cache_resource
def load_classifier():
    return pipeline(
        "zero-shot-classification",
        model="cross-encoder/nli-MiniLM2-L6-H768"
    )

def smart_categorize(description):
    desc_lower = description.lower()
    for keyword, category in KEYWORD_MAP.items():
        if keyword in desc_lower:
            return category
    try:
        classifier = load_classifier()
        result = classifier(description, categories)
        return result["labels"][0]
    except:
        return "Other"

def extract_text_from_image(image_bytes):
    image = Image.open(io.BytesIO(image_bytes))
    text = pytesseract.image_to_string(image)
    return text

def extract_text_from_pdf(pdf_bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    return full_text

def parse_transactions_from_pdf(text):
    transactions = []

    date_pattern = re.compile(r"\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}")
    amount_pattern = re.compile(r"\$?\d{1,3}(?:,\d{3})*\.\d{2}")

    dates = [(m.start(), m.end(), m.group()) for m in date_pattern.finditer(text)]
    amounts = [(m.start(), m.end(), m.group()) for m in amount_pattern.finditer(text)]

    for i, (d_start, d_end, date_str) in enumerate(dates):
        next_amount = None
        for a_start, a_end, amt_str in amounts:
            if a_start > d_start:
                next_amount = (a_start, a_end, amt_str)
                break

        if next_amount is None:
            continue

        a_start, a_end, amt_str = next_amount

        description = text[d_end:a_start].strip()
        description = re.sub(r"\s+", " ", description).strip()
        description = description.strip("$(),.-")

        if not description or len(description) < 2:
            description = "Unknown Transaction"

        amt_clean = amt_str.replace("$", "").replace(",", "")
        try:
            transactions.append({
                "date": date_str,
                "description": description,
                "amount": float(amt_clean)
            })
        except:
            continue

    return transactions

def parse_transactions_from_image(text):
    transactions = []

    text = text.replace("'", "").replace("`", "").replace("™", "")
    text = re.sub(r"\s+", " ", text)

    amount_pattern = re.compile(r"\$?\d{1,3}(?:,\d{3})*\.\d{2}")
    date_pattern = re.compile(r"\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}")

    dates = [(m.start(), m.group()) for m in date_pattern.finditer(text)]
    amounts = [(m.start(), m.group()) for m in amount_pattern.finditer(text)]

    for amt_pos, amt_str in amounts:
        best_date = None
        best_dist = 999999
        for date_pos, date_str in dates:
            dist = abs(amt_pos - date_pos)
            if dist < best_dist:
                best_dist = dist
                best_date = (date_pos, date_str)

        if best_date is None:
            best_date = (0, "01/01/2024")

        date_pos, date_str = best_date
        start = min(date_pos + len(date_str), amt_pos)
        end = max(date_pos + len(date_str), amt_pos)
        description = text[start:end].strip()
        description = re.sub(r"[$\d\.\,\/\-]", "", description).strip()
        description = re.sub(r"\s+", " ", description).strip()

        if not description or len(description) < 2:
            description = "Unknown Transaction"

        amt_clean = amt_str.replace("$", "").replace(",", "")
        try:
            transactions.append({
                "date": date_str,
                "description": description,
                "amount": float(amt_clean)
            })
        except:
            continue

    return transactions

def categorize_transactions(df):
    with st.spinner("AI is categorizing transactions..."):
        df["category"] = df["description"].apply(smart_categorize)
    return df

def show_dashboard(df):
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["amount"] = df["amount"].astype(float).abs()
    df = df.dropna(subset=["date"])

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Transactions", len(df))
    col2.metric("Total Spent", f"${df['amount'].sum():,.2f}")
    col3.metric("Date Range", f"{df['date'].min().strftime('%b %Y')} – {df['date'].max().strftime('%b %Y')}")

    st.divider()

    left, right = st.columns(2)
    with left:
        st.subheader("Spending by Category")
        cat_totals = df.groupby("category")["amount"].sum().reset_index()
        cat_totals = cat_totals.sort_values("amount", ascending=False)
        fig = px.pie(cat_totals, names="category", values="amount", hole=0.3)
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("Category Totals")
        display = cat_totals.copy()
        display["amount"] = display["amount"].apply(lambda x: f"${x:,.2f}")
        st.dataframe(display, use_container_width=True, hide_index=True)

    st.divider()

    st.subheader("🔁 Likely Recurring Charges")
    recurring = (
        df.groupby(["description", "amount"])
          .agg(times_charged=("date", "count"), last_seen=("date", "max"))
          .reset_index()
    )
    recurring = recurring[recurring["times_charged"] >= 2].sort_values("amount", ascending=False)
    if len(recurring) > 0:
        st.warning(f"Found {len(recurring)} recurring charges totalling **${recurring['amount'].sum():,.2f}**")
        display_r = recurring.copy()
        display_r["amount"] = display_r["amount"].apply(lambda x: f"${x:,.2f}")
        st.dataframe(display_r, use_container_width=True, hide_index=True)
    else:
        st.info("No recurring charges found")

    st.divider()

    with st.expander("📋 View all transactions"):
        st.dataframe(df, use_container_width=True, hide_index=True)

# ---- MAIN UI ----
st.write("Upload a **bank statement image**, **PDF**, or **CSV** to analyze your spending.")

upload_type = st.radio(
    "What are you uploading?",
    ["📸 Screenshot / Image", "📄 PDF Statement", "📊 CSV File"]
)

if upload_type == "📸 Screenshot / Image":
    uploaded = st.file_uploader("Upload screenshot of transactions", type=["png", "jpg", "jpeg"])
    if uploaded:
        st.image(uploaded, caption="Uploaded image", use_column_width=True)
        if st.button("Extract & Analyze Transactions"):
            with st.spinner("Reading text from image..."):
                text = extract_text_from_image(uploaded.read())
            with st.expander("Raw text extracted"):
                st.text(text)
            transactions = parse_transactions_from_image(text)
            if transactions:
                df = pd.DataFrame(transactions)
                df = categorize_transactions(df)
                st.success(f"✅ Found {len(df)} transactions!")
                show_dashboard(df)
            else:
                st.error("Could not find transactions. Make sure the image shows dates and amounts clearly.")

elif upload_type == "📄 PDF Statement":
    uploaded = st.file_uploader("Upload PDF bank statement", type=["pdf"])
    if uploaded:
        if st.button("Extract & Analyze Transactions"):
            with st.spinner("Reading text from PDF..."):
                text = extract_text_from_pdf(uploaded.read())
            with st.expander("Raw text extracted"):
                st.text(text[:2000])
            transactions = parse_transactions_from_pdf(text)
            if transactions:
                df = pd.DataFrame(transactions)
                df = categorize_transactions(df)
                st.success(f"✅ Found {len(df)} transactions!")
                show_dashboard(df)
            else:
                st.error("Could not find transactions in this PDF.")

elif upload_type == "📊 CSV File":
    uploaded = st.file_uploader("Upload CSV file", type=["csv"])
    if uploaded:
        df = pd.read_csv(uploaded)
        if "category" not in df.columns:
            df = categorize_transactions(df)
        st.success(f"✅ Loaded {len(df)} transactions!")
        show_dashboard(df)