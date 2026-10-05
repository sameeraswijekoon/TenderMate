from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.services.pdf_ocr import extract_pages
from app.services.tender_parser import parse_tender

app = FastAPI(title="TenderMate", version="0.1.0")

BASE = Path(__file__).resolve().parents[2]
FRONTEND = BASE / "frontend"

@app.get("/")
def home():
    return FileResponse(FRONTEND / "index.html")

@app.post("/api/analyze")
async def analyze_tender(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF file.")

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="The uploaded PDF is empty.")
    if len(data) > 100 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="PDF is larger than 100 MB.")

    try:
        pages = extract_pages(data)
        summary = parse_tender(pages)
        return {
            "filename": file.filename,
            "page_count": len(pages),
            "summary": summary.model_dump(),
            "pages": pages,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unable to process PDF: {exc}")
