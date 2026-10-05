import asyncio
import time
import uuid
from pathlib import Path
from threading import Lock

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from app.services.pdf_ocr import extract_pages
from app.services.tender_parser import parse_tender, extract_requirements, detect_risks
from app.services.storage import init_db, save_tender, list_tenders, get_tender
from app.services.exporter import tender_xlsx
from app.services.addendum import compare_pages
from app.services.product_matcher import match_products
from app.services.compliance import build_compliance
from app.services.sync import sync_google_sheets, sync_firebase

app = FastAPI(title="TenderMate – IT Pre-Sales Assistant", version="1.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False, allow_methods=["*"], allow_headers=["*"])
BASE = Path(__file__).resolve().parents[2]
FRONTEND = BASE / "frontend"
init_db()

JOBS = {}
JOBS_LOCK = Lock()
MAX_PDF_BYTES = 100 * 1024 * 1024


@app.get("/")
def home():
    return FileResponse(FRONTEND / "index.html")


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "app": "TenderMate",
        "version": "1.1.0",
        "ocr_workers": 4,
        "features": ["background_jobs", "parallel_ocr", "page_progress", "speed_eta"],
    }


@app.post("/api/sync/{tender_id}")
def sync(tender_id: int):
    p = get_tender(tender_id)
    if not p:
        raise HTTPException(404, "Tender not found")
    return {"google_sheets": sync_google_sheets(p), "firebase": sync_firebase(p)}


def _set_job(job_id, **updates):
    with JOBS_LOCK:
        if job_id in JOBS:
            JOBS[job_id].update(updates)


def _job_progress(job_id, info):
    _set_job(job_id, progress=info)


def _process_tender(data, filename, job_id=None, save=False):
    callback = (lambda info: _job_progress(job_id, info)) if job_id else None
    started = time.time()

    if job_id:
        _set_job(job_id, status="reading", message="Reading PDF pages...", started_at=started)

    pages = extract_pages(data, progress=callback)
    if job_id:
        _set_job(job_id, status="analyzing", message="Extracting tender fields and requirements...")

    summary = parse_tender(pages)
    requirements = extract_requirements(pages)
    payload = {
        "filename": filename,
        "page_count": len(pages),
        "summary": summary.model_dump(),
        "requirements": [x.model_dump() for x in requirements],
        "risks": detect_risks(summary, pages),
        "pages": pages,
    }

    if save:
        payload["id"] = save_tender(payload)

    if job_id:
        _set_job(
            job_id,
            status="complete",
            message="Tender analysis complete.",
            progress={
                **(JOBS[job_id].get("progress") or {}),
                "phase": "complete",
                "completed_pages": len(pages),
                "total_pages": len(pages),
                "elapsed": round(time.time() - started, 1),
            },
            result=payload,
            finished_at=time.time(),
        )
    return payload


async def analyze_bytes(data, filename):
    return await asyncio.to_thread(_process_tender, data, filename)


@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Please upload a PDF file.")
    data = await file.read()
    if not data:
        raise HTTPException(400, "The uploaded PDF is empty.")
    if len(data) > MAX_PDF_BYTES:
        raise HTTPException(413, "PDF is larger than 100 MB.")
    try:
        return await analyze_bytes(data, file.filename)
    except Exception as e:
        raise HTTPException(500, f"Unable to process PDF: {e}")


@app.post("/api/tenders/start")
async def start_tender(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Please upload a PDF file.")
    data = await file.read()
    if not data:
        raise HTTPException(400, "The uploaded PDF is empty.")
    if len(data) > MAX_PDF_BYTES:
        raise HTTPException(413, "PDF is larger than 100 MB.")

    job_id = uuid.uuid4().hex[:12]
    with JOBS_LOCK:
        JOBS[job_id] = {
            "id": job_id,
            "status": "queued",
            "message": "Waiting for an OCR worker...",
            "filename": file.filename,
            "progress": {
                "phase": "queued",
                "current_page": 0,
                "total_pages": 0,
                "completed_pages": 0,
                "text_pages": 0,
                "ocr_pages": 0,
                "ocr_total": 0,
                "speed_pages_per_min": 0,
                "eta_seconds": None,
            },
            "created_at": time.time(),
        }

    asyncio.create_task(asyncio.to_thread(_process_tender, data, file.filename, job_id, True))
    return {"job_id": job_id}


@app.get("/api/jobs/{job_id}")
def job_status(job_id: str):
    with JOBS_LOCK:
        job = JOBS.get(job_id)
        if not job:
            raise HTTPException(404, "Analysis job not found.")
        return dict(job)


@app.delete("/api/jobs/{job_id}")
def delete_job(job_id: str):
    with JOBS_LOCK:
        JOBS.pop(job_id, None)
    return {"status": "deleted"}


@app.post("/api/tenders")
async def create_tender(file: UploadFile = File(...)):
    data = await file.read()
    if len(data) > MAX_PDF_BYTES:
        raise HTTPException(413, "PDF is larger than 100 MB.")
    try:
        return await asyncio.to_thread(_process_tender, data, file.filename, None, True)
    except Exception as e:
        raise HTTPException(500, f"Unable to process PDF: {e}")


@app.get("/api/tenders")
def tenders():
    return list_tenders()


@app.get("/api/tenders/{tender_id}")
def tender(tender_id: int):
    p = get_tender(tender_id)
    if not p:
        raise HTTPException(404, "Tender not found")
    return p


@app.post("/api/export")
async def export(file: UploadFile = File(...)):
    p = await analyze_bytes(await file.read(), file.filename)
    out = tender_xlsx(p)
    return StreamingResponse(
        out,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{Path(file.filename).stem}_TenderMate.xlsx"'},
    )


@app.post("/api/compare-addendum")
async def compare(old_file: UploadFile = File(...), new_file: UploadFile = File(...)):
    old = await analyze_bytes(await old_file.read(), old_file.filename)
    new = await analyze_bytes(await new_file.read(), new_file.filename)
    return {
        "old_pages": len(old["pages"]),
        "new_pages": len(new["pages"]),
        "changes": compare_pages(old["pages"], new["pages"]),
    }


@app.post("/api/product-match")
async def product_match(file: UploadFile = File(...)):
    p = await analyze_bytes(await file.read(), file.filename)
    text = "\n".join(x["text"] for x in p["pages"])
    return {"matches": match_products(text), "filename": file.filename}


@app.post("/api/compliance")
async def compliance(file: UploadFile = File(...), offered_text: str = Form("")):
    p = await analyze_bytes(await file.read(), file.filename)
    return {"items": build_compliance(p["requirements"], offered_text), "requirements": p["requirements"]}
