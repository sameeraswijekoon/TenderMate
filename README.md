# TenderMate – IT Pre-Sales Assistant

TenderMate is a local-first tender PDF assistant for IT pre-sales work.

## MVP

Upload one tender PDF. TenderMate:
1. Reads every page.
2. Uses native PDF text when available.
3. Automatically falls back to OCR for scanned/image pages.
4. Extracts common tender dates, quantities, warranty, delivery, validity, locations and required documents.
5. Keeps page references for verification.
6. Shows the result in a simple browser UI.

## Run

### Windows / local
Install Python 3.11+ and Tesseract OCR.

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000

### Docker
```bash
docker compose up --build
```

## Project structure

- `backend/app/main.py` - FastAPI API
- `backend/app/services/pdf_ocr.py` - page extraction + OCR
- `backend/app/services/tender_parser.py` - tender field extraction
- `backend/app/models/tender.py` - response models
- `frontend/index.html` - upload and summary UI

## Next modules

Technical specification extraction, compliance matrix, addendum comparison, document checklist, tender deadline dashboard, pricing/SPR workflow and Firebase/Google Sheets persistence.
