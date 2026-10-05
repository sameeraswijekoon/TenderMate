# TenderMate – IT Pre-Sales Assistant

TenderMate is a local-first tender intelligence tool for IT pre-sales teams.

## What is included

### 1. Tender analyzer
Upload one tender PDF and TenderMate processes every page. Native PDF text is used when available and scanned pages automatically go through Tesseract OCR.

### 2. Tender summary
Extracts common tender information with source page and confidence:
- Tender title / reference
- Closing date and time
- Pre-bid date, time and location
- Submission location
- Delivery period
- Bid validity
- Quantity
- Warranty
- Bid security
- Performance security
- Required documents

### 3. Technical / requirement extraction
Detects lines that look like mandatory specifications, certificates, eligibility, delivery and document requirements.

### 4. Compliance matrix
Paste an offered model/specification and generate a requirement-by-requirement review. Results are intentionally marked for manual verification rather than pretending that uncertain matches are compliant.

### 5. Addendum comparison
Upload the original tender and an addendum/revised tender. TenderMate compares page text and identifies changed pages.

### 6. Product matching
The backend includes an initial IT product catalog matcher for common Lenovo and HP business models. The catalog is designed to be expanded with your real MTM/SKU data.

### 7. Risk flags
Flags missing critical tender fields and warns when OCR was used.

### 8. Tender dashboard
Analyzed tenders can be saved in a local SQLite database and listed from the dashboard.

### 9. Excel export
Exports Tender Summary, Requirements and Risks to XLSX.

### 10. Cloud fallback hooks
Optional Google Sheets and Firebase synchronization can be enabled with HTTPS webhook environment variables. Local SQLite remains the primary offline source.

### 11. API
- `POST /api/analyze`
- `POST /api/tenders`
- `GET /api/tenders`
- `GET /api/tenders/{id}`
- `POST /api/export`
- `POST /api/compare-addendum`
- `POST /api/product-match`
- `POST /api/compliance`
- `POST /api/sync/{id}`

## Run locally

### Windows

Install Python 3.11+ and Tesseract OCR.

```bat
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open http://127.0.0.1:8000

### Docker

```bash
docker compose up --build
```

## Optional sync

Set:
- `GOOGLE_SHEETS_WEBHOOK_URL`
- `FIREBASE_WEBHOOK_URL`

These are intentionally webhook-based so credentials are not stored in source code.

## Architecture

```
PDF Upload
   ↓
Page Extraction
   ↓
OCR fallback for scanned pages
   ↓
Page-level text store
   ↓
Tender Parser
   ├── Summary
   ├── Requirements
   ├── Risk Flags
   └── Source Pages
        ↓
Dashboard / Compliance / Addendum / Product Match / Excel
        ↓
SQLite + optional Google Sheets / Firebase
```

## Roadmap

The next production hardening steps are stronger AI-assisted specification extraction, a maintained Lenovo/HP/Dell/ASUS/Acer catalog, exact numeric compliance rules, tender deadline alerts, user authentication and role-based access, and direct Google Sheets/Firebase connectors instead of webhook adapters.
