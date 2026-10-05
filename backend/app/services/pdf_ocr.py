import io
import re
import fitz
import pytesseract
from PIL import Image

def extract_pages(pdf_bytes: bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages = []

    for page_no, page in enumerate(doc, start=1):
        text = page.get_text("text").strip()

        # Scanned/image page: render and OCR it.
        if len(re.sub(r"\s+", "", text)) < 40:
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
            image = Image.open(io.BytesIO(pix.tobytes("png")))
            text = pytesseract.image_to_string(image, lang="eng").strip()
            method = "ocr"
        else:
            method = "text"

        pages.append({
            "page": page_no,
            "text": text,
            "method": method,
        })

    return pages
