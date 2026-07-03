# 💰 Spending Auditor

An AI-powered personal finance dashboard that automatically extracts and categorizes transactions from bank statements uploaded as CSV, PDF, or images.

**Live Demo:** [spending-auditor.vercel.app](https://spending-auditor.vercel.app)

---

## Features

- **3 upload modes** — CSV exports, PDF bank statements, and screenshots/images
- **Smart categorization** — keyword-based AI classification across 12 categories (Groceries, Dining, Transport, Entertainment, UPI Transfers, and more) with support for Indian merchants (Zomato, Swiggy, DMart, Jio, Ola, PhonePe, etc.)
- **OCR for images** — Tesseract OCR extracts transaction text from bank app screenshots
- **PDF parsing** — PyMuPDF extracts text from digital bank statement PDFs
- **Dashboard analytics** — donut chart, category totals, recurring charge detection, full transaction table
- **Recurring charge detection** — automatically flags subscriptions and repeated payments

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React, Vite, Tailwind CSS, Recharts |
| Backend | Python, FastAPI, Uvicorn |
| PDF Extraction | PyMuPDF (fitz) |
| Image OCR | Tesseract OCR, pytesseract, Pillow |
| Data Processing | Pandas |
| Frontend Hosting | Vercel |
| Backend Hosting | Railway |

---

## How It Works

1. User uploads a bank statement (CSV / PDF / image)
2. FastAPI backend receives the file and extracts raw text
   - CSV: read directly with Pandas
   - PDF: PyMuPDF extracts text from digital PDFs
   - Image: Tesseract OCR reads text from screenshots
3. Custom regex parser identifies dates, amounts, and descriptions
4. Keyword-based categorization maps merchants to spending categories
5. React frontend renders the dashboard with charts and tables

---

## Project Structure

```
spending-auditor/
├── backend/
│   ├── main.py              # FastAPI app with 3 upload endpoints
│   ├── app.py               # Original Streamlit version (for reference)
│   ├── clean.py             # CSV cleaning utilities
│   ├── categorize.py        # Standalone categorization script
│   ├── explore.py           # Data exploration utilities
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile           # Docker config for Railway deployment
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Root component with page routing
│   │   ├── components/
│   │   │   ├── Upload.jsx   # Upload page with drag-and-drop
│   │   │   ├── Dashboard.jsx # Analytics dashboard
│   │   │   └── SplashCursor.jsx # Mouse trail effect
│   │   └── index.css        # Global styles
│   ├── package.json
│   └── vite.config.js
└── start.bat                # One-click local startup script
```

---

## Running Locally

### Prerequisites
- Python 3.10+
- Node.js 18+
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) installed

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
uvicorn main:app --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

> **Note:** Update `const API` in `frontend/src/components/Upload.jsx` to `http://127.0.0.1:8000` for local development.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/upload/csv` | Upload CSV bank export |
| POST | `/upload/pdf` | Upload PDF bank statement |
| POST | `/upload/image` | Upload bank screenshot |

All endpoints return a JSON array of transaction objects:
```json
[
  {
    "date": "2024-01-03",
    "description": "Netflix",
    "amount": 15.99,
    "category": "Streaming and Subscriptions"
  }
]
```

---

## Supported Categories

- Groceries and Daily Needs
- Food Delivery and Dining
- Streaming and Subscriptions
- Transport and Fuel
- Travel and Hotels
- Shopping and Fashion
- Health and Medical
- Recharge and Bills
- Education
- Entertainment
- UPI and Transfers
- Other

---

## Sample Test Files

Sample bank statements are included in `backend/` for testing:
- `sample_transactions.csv` — 20 realistic transactions
- `sample_bank_statement.pdf` — PDF bank statement
- `bank_screenshot.png` — Bank app screenshot

---

## Author

**Purva** — [GitHub](https://github.com/purvateli2023-rgb)

---

*Project 1 of 3 planned portfolio projects. Next: Game Recommender, Fridge-to-Recipe Generator.*