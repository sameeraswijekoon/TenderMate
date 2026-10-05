import io
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import fitz
import pytesseract
from PIL import Image


def _ocr_image(image_bytes):
    img = Image.open(io.BytesIO(image_bytes))
    return pytesseract.image_to_string(img, lang="eng", config="--psm 6").strip()


def extract_pages(pdf_bytes, progress=None):
    """
    Fast page pipeline:
    1. Extract native text from every page first.
    2. Only render pages that actually need OCR.
    3. OCR scanned pages in parallel using Tesseract worker processes.
    """
    started = time.time()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    total = len(doc)
    pages = [None] * total
    scanned = []

    # Native text extraction is much faster than OCR, so do this pass first.
    for idx, page in enumerate(doc):
        native = page.get_text("text").strip()
        if len(re.sub(r"\s+", "", native)) < 40:
            scanned.append(idx)
            pages[idx] = {"page": idx + 1, "text": "", "method": "pending_ocr"}
        else:
            pages[idx] = {"page": idx + 1, "text": native, "method": "text"}

    if progress:
        progress({
            "phase": "page_scan",
            "current_page": total,
            "total_pages": total,
            "completed_pages": total - len(scanned),
            "text_pages": total - len(scanned),
            "ocr_pages": 0,
            "ocr_total": len(scanned),
            "elapsed": round(time.time() - started, 1),
        })

    workers = max(1, min(int(os.getenv("TENDERMATE_OCR_WORKERS", "4")), 8))
    scale = float(os.getenv("TENDERMATE_OCR_SCALE", "1.8"))

    completed_ocr = 0
    if scanned:
        # Keep the number of queued images bounded so a 200-page scan does not
        # consume hundreds of MB of RAM before OCR starts.
        batch_size = workers * 2
        for start in range(0, len(scanned), batch_size):
            batch = scanned[start:start + batch_size]
            futures = {}
            for idx in batch:
                pix = doc[idx].get_pixmap(
                    matrix=fitz.Matrix(scale, scale),
                    alpha=False,
                    colorspace=fitz.csRGB,
                )
                futures[_submit_ocr(pix.tobytes("jpg"), workers)] = idx

            for future in as_completed(futures):
                idx = futures[future]
                try:
                    text = future.result()
                except Exception as exc:
                    text = f"[OCR ERROR: {exc}]"
                pages[idx] = {"page": idx + 1, "text": text, "method": "ocr"}
                completed_ocr += 1

                if progress:
                    elapsed = max(time.time() - started, 0.1)
                    speed = completed_ocr / elapsed * 60
                    remaining = len(scanned) - completed_ocr
                    progress({
                        "phase": "ocr",
                        "current_page": idx + 1,
                        "total_pages": total,
                        "completed_pages": total - len(scanned) + completed_ocr,
                        "text_pages": total - len(scanned),
                        "ocr_pages": completed_ocr,
                        "ocr_total": len(scanned),
                        "speed_pages_per_min": round(speed, 1),
                        "eta_seconds": round(remaining / max(speed / 60, 0.001), 1),
                        "elapsed": round(time.time() - started, 1),
                    })

    doc.close()

    if progress:
        elapsed = max(time.time() - started, 0.1)
        progress({
            "phase": "complete",
            "current_page": total,
            "total_pages": total,
            "completed_pages": total,
            "text_pages": total - len(scanned),
            "ocr_pages": len(scanned),
            "ocr_total": len(scanned),
            "speed_pages_per_min": round(total / elapsed * 60, 1),
            "elapsed": round(elapsed, 1),
        })

    return pages


_EXECUTOR = None


def _submit_ocr(image_bytes, workers):
    global _EXECUTOR
    if _EXECUTOR is None:
        _EXECUTOR = ThreadPoolExecutor(max_workers=workers, thread_name_prefix="tendermate-ocr")
    return _EXECUTOR.submit(_ocr_image, image_bytes)
