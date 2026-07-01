from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import pytesseract
from PIL import Image, ImageEnhance
import fitz
import io
import re

pytesseract.pytesseract.tesseract_cmd = r"C:\Users\pur03\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"


def clean_csv(df):
    df = df.rename(columns={
        "Date": "date",
        "Transaction Description": "description",
        "Amount": "amount"
    })
    df = df[["date", "description", "amount"]]
    df["amount"] = (
        df["amount"]
        .astype(str)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .astype(float)
    )
    df["amount"] = df["amount"].abs()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    return df


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    "wholefood": "Groceries and Supermarkets",
    "trader joe": "Groceries and Supermarkets",
    "kroger": "Groceries and Supermarkets",
    "target": "Groceries and Supermarkets",
    "uber": "Transport and Fuel and Gas Station",
    "lyft": "Transport and Fuel and Gas Station",
    "shell": "Transport and Fuel and Gas Station",
    "gas": "Transport and Fuel and Gas Station",
    "mcdonald": "Dining and Restaurants and Food Delivery",
    "starbucks": "Dining and Restaurants and Food Delivery",
    "domino": "Dining and Restaurants and Food Delivery",
    "chipotle": "Dining and Restaurants and Food Delivery",
    "pizza": "Dining and Restaurants and Food Delivery",
    "doordash": "Dining and Restaurants and Food Delivery",
    "grubhub": "Dining and Restaurants and Food Delivery",
    "subway": "Dining and Restaurants and Food Delivery",
    "electricity": "Utilities and Bills and Electricity and Water",
    "water bill": "Utilities and Bills and Electricity and Water",
    "cvs": "Health and Pharmacy and Medical",
    "pharmacy": "Health and Pharmacy and Medical",
    "walgreens": "Health and Pharmacy and Medical",
    "zara": "Shopping and Clothing and Fashion",
    "nike": "Shopping and Clothing and Fashion",
    "adidas": "Shopping and Clothing and Fashion",
    "amazon": "Shopping and Clothing and Fashion",
    "apple": "Entertainment and Gaming",
    "google": "Entertainment and Gaming",
    "steam": "Entertainment and Gaming",
    "playstation": "Entertainment and Gaming",
    "xbox": "Entertainment and Gaming",
}


def smart_categorize(description):
    desc_lower = description.lower()
    for keyword, category in KEYWORD_MAP.items():
        if keyword in desc_lower:
            return category
    return "Other"


def extract_text_from_image(image_bytes):
    image = Image.open(io.BytesIO(image_bytes))
    image = image.convert("L")
    w, h = image.size
    image = image.resize((w * 2, h * 2), Image.LANCZOS)
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)
    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(image, config=custom_config)
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
        except Exception:
            continue
    return transactions


def parse_transactions_from_image(text):
    transactions = []

    lines = text.strip().split('\n')

    date_pattern = re.compile(r"\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}")
    amount_pattern = re.compile(r"\$?\d{1,3}(?:,\d{3})*\.\d{2}")

    for line in lines:
        line = line.strip()
        if not line:
            continue

        date_match = date_pattern.search(line)
        amount_match = amount_pattern.search(line)

        if not date_match or not amount_match:
            continue

        date_str = date_match.group()
        amt_str = amount_match.group()

        start = date_match.end()
        end = amount_match.start()

        if end > start:
            description = line[start:end].strip()
        else:
            description = line[date_match.end():].replace(amt_str, "").strip()

        description = re.sub(r"[$\d\.\,\/\-]", "", description).strip()
        description = re.sub(r"\s+", " ", description).strip()
        description = description.strip("$(),.-*|")

        if not description or len(description) < 2:
            description = "Unknown Transaction"

        amt_clean = amt_str.replace("$", "").replace(",", "")
        try:
            transactions.append({
                "date": date_str,
                "description": description,
                "amount": float(amt_clean)
            })
        except Exception:
            continue

    return transactions


def categorize_transactions(df):
    df["category"] = df["description"].apply(smart_categorize)
    return df


@app.get("/")
def root():
    return {"status": "Spending Auditor API is running"}


@app.post("/upload/csv")
async def upload_csv(file: UploadFile = File(...)):
    contents = await file.read()
    df = pd.read_csv(io.BytesIO(contents))
    if "description" not in df.columns:
        df = clean_csv(df)
    if "category" not in df.columns:
        df = categorize_transactions(df)
    return df.to_dict(orient="records")


@app.post("/upload/pdf")
async def upload_pdf(file: UploadFile = File(...)):
    contents = await file.read()
    text = extract_text_from_pdf(contents)
    transactions = parse_transactions_from_pdf(text)
    if not transactions:
        return {"error": "Could not find transactions in this PDF."}
    df = pd.DataFrame(transactions)
    df = categorize_transactions(df)
    return df.to_dict(orient="records")


@app.post("/upload/image")
async def upload_image(file: UploadFile = File(...)):
    contents = await file.read()
    text = extract_text_from_image(contents)
    transactions = parse_transactions_from_image(text)
    if not transactions:
        return {"error": "Could not find transactions. Make sure the image shows dates and amounts clearly."}
    df = pd.DataFrame(transactions)
    df = categorize_transactions(df)
    return df.to_dict(orient="records")