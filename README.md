# AP Audit Gateway

Automated Accounts Payable audit gateway for invoice ingestion, structured extraction, historical duplicate detection, price anomaly analysis, and explainable payment risk scoring.

## Features
- PDF/image invoice ingestion
- PDF text extraction with PyMuPDF
- Optional image OCR with Tesseract
- SQLite transaction history
- Exact and fuzzy duplicate invoice detection
- Historical unit-price anomaly detection
- Vendor, quantity, and payment anomaly signals
- Explainable 0-100 risk score
- FastAPI REST API

## Run locally

    python -m venv .venv
    pip install -r requirements.txt
    uvicorn app.main:app --reload

Open http://127.0.0.1:8000/docs.

## API
- POST /invoices/audit
- POST /transactions
- GET /transactions
- GET /health

Risk levels: LOW 0-30, MEDIUM 31-60, HIGH 61-80, CRITICAL 81-100.
