import os
import platform
import io
import re

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import pytesseract
from PIL import Image, ImageEnhance
import fitz

if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Users\pur03\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
else:
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"


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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

categories = [
    "Groceries and Daily Needs",
    "Food Delivery and Dining",
    "Streaming and Subscriptions",
    "Transport and Fuel",
    "Travel and Hotels",
    "Shopping and Fashion",
    "Health and Medical",
    "Recharge and Bills",
    "Education",
    "Entertainment",
    "UPI and Transfers",
    "Other"
]

KEYWORD_MAP = {
    # --- GROCERIES AND DAILY NEEDS ---
    "dmart": "Groceries and Daily Needs",
    "d-mart": "Groceries and Daily Needs",
    "reliance fresh": "Groceries and Daily Needs",
    "reliance smart": "Groceries and Daily Needs",
    "bigbasket": "Groceries and Daily Needs",
    "big basket": "Groceries and Daily Needs",
    "zepto": "Groceries and Daily Needs",
    "blinkit": "Groceries and Daily Needs",
    "grofers": "Groceries and Daily Needs",
    "instamart": "Groceries and Daily Needs",
    "walmart": "Groceries and Daily Needs",
    "costco": "Groceries and Daily Needs",
    "whole foods": "Groceries and Daily Needs",
    "trader joe": "Groceries and Daily Needs",
    "kroger": "Groceries and Daily Needs",
    "target": "Groceries and Daily Needs",
    "nature basket": "Groceries and Daily Needs",
    "super market": "Groceries and Daily Needs",
    "supermarket": "Groceries and Daily Needs",
    "kirana": "Groceries and Daily Needs",
    "grocery": "Groceries and Daily Needs",

    # --- FOOD DELIVERY AND DINING ---
    "zomato": "Food Delivery and Dining",
    "swiggy": "Food Delivery and Dining",
    "doordash": "Food Delivery and Dining",
    "grubhub": "Food Delivery and Dining",
    "mcdonald": "Food Delivery and Dining",
    "mcdonalds": "Food Delivery and Dining",
    "starbucks": "Food Delivery and Dining",
    "domino": "Food Delivery and Dining",
    "chipotle": "Food Delivery and Dining",
    "pizza": "Food Delivery and Dining",
    "subway": "Food Delivery and Dining",
    "kfc": "Food Delivery and Dining",
    "burger king": "Food Delivery and Dining",
    "burger": "Food Delivery and Dining",
    "restaurant": "Food Delivery and Dining",
    "cafe": "Food Delivery and Dining",
    "dhaba": "Food Delivery and Dining",
    "hotel restaurant": "Food Delivery and Dining",
    "biryani": "Food Delivery and Dining",
    "chai": "Food Delivery and Dining",
    "canteen": "Food Delivery and Dining",
    "food stall": "Food Delivery and Dining",
    "mess": "Food Delivery and Dining",
    "bakery": "Food Delivery and Dining",
    "haldiram": "Food Delivery and Dining",
    "barbeque": "Food Delivery and Dining",
    "bbq": "Food Delivery and Dining",
    "eat": "Food Delivery and Dining",
    "hungry": "Food Delivery and Dining",
    "dunkin": "Food Delivery and Dining",
    "baskin": "Food Delivery and Dining",

    # --- STREAMING AND SUBSCRIPTIONS ---
    "netflix": "Streaming and Subscriptions",
    "spotify": "Streaming and Subscriptions",
    "amazon prime": "Streaming and Subscriptions",
    "hulu": "Streaming and Subscriptions",
    "disney": "Streaming and Subscriptions",
    "hotstar": "Streaming and Subscriptions",
    "zee5": "Streaming and Subscriptions",
    "sonyliv": "Streaming and Subscriptions",
    "sony liv": "Streaming and Subscriptions",
    "jiocinema": "Streaming and Subscriptions",
    "jio cinema": "Streaming and Subscriptions",
    "voot": "Streaming and Subscriptions",
    "mxplayer": "Streaming and Subscriptions",
    "mx player": "Streaming and Subscriptions",
    "youtube premium": "Streaming and Subscriptions",
    "apple tv": "Streaming and Subscriptions",
    "subscription": "Streaming and Subscriptions",

    # --- TRANSPORT AND FUEL ---
    "uber": "Transport and Fuel",
    "ola": "Transport and Fuel",
    "lyft": "Transport and Fuel",
    "rapido": "Transport and Fuel",
    "shell": "Transport and Fuel",
    "petrol": "Transport and Fuel",
    "diesel": "Transport and Fuel",
    "fuel": "Transport and Fuel",
    "hpcl": "Transport and Fuel",
    "bpcl": "Transport and Fuel",
    "iocl": "Transport and Fuel",
    "indian oil": "Transport and Fuel",
    "hp petrol": "Transport and Fuel",
    "bharat petroleum": "Transport and Fuel",
    "metro": "Transport and Fuel",
    "mumbai metro": "Transport and Fuel",
    "best bus": "Transport and Fuel",
    "bus pass": "Transport and Fuel",
    "rickshaw": "Transport and Fuel",
    "auto": "Transport and Fuel",
    "cab": "Transport and Fuel",
    "taxi": "Transport and Fuel",
    "parking": "Transport and Fuel",
    "fastag": "Transport and Fuel",
    "toll": "Transport and Fuel",
    "irctc": "Travel and Hotels",

    # --- TRAVEL AND HOTELS ---
    "hotel": "Travel and Hotels",
    "taj": "Travel and Hotels",
    "oberoi": "Travel and Hotels",
    "marriott": "Travel and Hotels",
    "hilton": "Travel and Hotels",
    "oyo": "Travel and Hotels",
    "makemytrip": "Travel and Hotels",
    "goibibo": "Travel and Hotels",
    "yatra": "Travel and Hotels",
    "cleartrip": "Travel and Hotels",
    "indigo": "Travel and Hotels",
    "air india": "Travel and Hotels",
    "spicejet": "Travel and Hotels",
    "vistara": "Travel and Hotels",
    "akasa": "Travel and Hotels",
    "flight": "Travel and Hotels",
    "airline": "Travel and Hotels",
    "airways": "Travel and Hotels",
    "resort": "Travel and Hotels",
    "lodge": "Travel and Hotels",
    "inn": "Travel and Hotels",

    # --- SHOPPING AND FASHION ---
    "amazon": "Shopping and Fashion",
    "flipkart": "Shopping and Fashion",
    "myntra": "Shopping and Fashion",
    "ajio": "Shopping and Fashion",
    "meesho": "Shopping and Fashion",
    "nykaa": "Shopping and Fashion",
    "snapdeal": "Shopping and Fashion",
    "tata cliq": "Shopping and Fashion",
    "zara": "Shopping and Fashion",
    "nike": "Shopping and Fashion",
    "adidas": "Shopping and Fashion",
    "puma": "Shopping and Fashion",
    "h&m": "Shopping and Fashion",
    "westside": "Shopping and Fashion",
    "pantaloons": "Shopping and Fashion",
    "shoppers stop": "Shopping and Fashion",
    "lifestyle": "Shopping and Fashion",
    "decathlon": "Shopping and Fashion",

    # --- HEALTH AND MEDICAL ---
    "apollo": "Health and Medical",
    "medplus": "Health and Medical",
    "netmeds": "Health and Medical",
    "pharmeasy": "Health and Medical",
    "1mg": "Health and Medical",
    "tata 1mg": "Health and Medical",
    "cvs": "Health and Medical",
    "pharmacy": "Health and Medical",
    "walgreens": "Health and Medical",
    "hospital": "Health and Medical",
    "clinic": "Health and Medical",
    "doctor": "Health and Medical",
    "medical": "Health and Medical",
    "diagnostic": "Health and Medical",
    "lab": "Health and Medical",
    "pathology": "Health and Medical",
    "chemist": "Health and Medical",
    "drugstore": "Health and Medical",

    # --- RECHARGE AND BILLS ---
    "jio": "Recharge and Bills",
    "airtel": "Recharge and Bills",
    "vodafone": "Recharge and Bills",
    "vi ": "Recharge and Bills",
    "bsnl": "Recharge and Bills",
    "recharge": "Recharge and Bills",
    "electricity": "Recharge and Bills",
    "mseb": "Recharge and Bills",
    "mahadiscom": "Recharge and Bills",
    "bescom": "Recharge and Bills",
    "water bill": "Recharge and Bills",
    "gas bill": "Recharge and Bills",
    "mahanagar gas": "Recharge and Bills",
    "mgl": "Recharge and Bills",
    "broadband": "Recharge and Bills",
    "wifi": "Recharge and Bills",
    "internet": "Recharge and Bills",
    "dth": "Recharge and Bills",
    "tata sky": "Recharge and Bills",
    "dish tv": "Recharge and Bills",
    "utility": "Recharge and Bills",
    "bill payment": "Recharge and Bills",
    "postpaid": "Recharge and Bills",

    # --- EDUCATION ---
    "school": "Education",
    "college": "Education",
    "university": "Education",
    "tuition": "Education",
    "byju": "Education",
    "unacademy": "Education",
    "coursera": "Education",
    "udemy": "Education",
    "vedantu": "Education",
    "toppr": "Education",
    "fees": "Education",
    "exam": "Education",
    "books": "Education",
    "stationery": "Education",

    # --- ENTERTAINMENT ---
    "bookmyshow": "Entertainment",
    "pvr": "Entertainment",
    "inox": "Entertainment",
    "cinepolis": "Entertainment",
    "cinema": "Entertainment",
    "movie": "Entertainment",
    "theatre": "Entertainment",
    "concert": "Entertainment",
    "event": "Entertainment",
    "gaming": "Entertainment",
    "steam": "Entertainment",
    "playstation": "Entertainment",
    "xbox": "Entertainment",
    "apple": "Entertainment",
    "google play": "Entertainment",

    # --- UPI AND TRANSFERS ---
    "phonepe": "UPI and Transfers",
    "gpay": "UPI and Transfers",
    "google pay": "UPI and Transfers",
    "paytm": "UPI and Transfers",
    "upi": "UPI and Transfers",
    "neft": "UPI and Transfers",
    "imps": "UPI and Transfers",
    "rtgs": "UPI and Transfers",
    "transfer": "UPI and Transfers",
    "sent to": "UPI and Transfers",
    "received from": "UPI and Transfers",
    "atm": "UPI and Transfers",
    "cash withdrawal": "UPI and Transfers",
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