# TenderMate – IT Pre-Sales Assistant

TenderMate is a GitHub Pages, browser-based tender intelligence tool for IT pre-sales teams.

## GitHub Pages mode

The main TenderMate application runs entirely in the browser.

- No FastAPI required
- No Python required
- No local server required
- No Docker required
- PDF processing happens locally in the browser
- Browser OCR uses Tesseract.js
- PDF reading uses PDF.js
- Excel export uses SheetJS
- Last analyzed tender can be stored in browser localStorage

Open the app from GitHub Pages and upload a tender PDF.

## Tender analyzer

TenderMate reads every PDF page directly in the browser.

1. Native PDF text is extracted first.
2. Pages with little/no native text are sent to browser OCR.
3. Tender pages are scored for relevance using terms such as closing date, pre-bid, technical specifications, warranty, delivery, bid security, eligibility, price schedule, submission, processor, RAM, storage, display, USB and PCIe.
4. A live progress monitor shows pages processed, OCR pages, speed, ETA and relevant-page count.

## Tender summary

Extracts common tender information from the browser-processed text:

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

## Requirement extraction

Detects lines that look like mandatory tender requirements, specifications, certificates, eligibility, delivery and document requirements.

Each detected requirement keeps its source page.

## Browser compliance review

Paste the offered model/specification and generate a requirement-by-requirement review. Results are deliberately marked for review rather than claiming uncertain matches are compliant.

## Excel export

Exports Tender Summary, Requirements and Risks to an XLSX file directly from the browser.

## Local browser dashboard

The latest analyzed tender is stored in browser localStorage so the GitHub Pages app can show the last analysis without a backend database.

## Important limitation

GitHub Pages is static hosting, so Python/FastAPI cannot run there. The GitHub Pages version therefore uses browser technologies instead:

GitHub Pages → TenderMate JavaScript → PDF.js → native PDF text → Tesseract.js OCR → tender parser → summary/requirements/risks → Excel export

For very large scanned tenders, OCR speed depends on the user's CPU, browser and PDF complexity. Keep the browser tab open while processing.

## Repository

https://github.com/sameeraswijekoon/TenderMate

## Main application

https://sameeraswijekoon.github.io/TenderMate/

## Future production improvements

- Smart relevance-first OCR so only high-value scanned pages receive deep OCR
- Better table/specification extraction
- Exact numeric compliance rules for CPU, RAM, storage, display, ports, PSU, warranty, etc.
- Page thumbnails and click-to-source-page navigation
- Sinhala/Tamil OCR language support
- Lenovo/HP/Dell/ASUS/Acer MTM/SKU catalog
- Tender deadline reminders
- Google Sheets / Firebase cloud persistence when required
- AI-assisted tender interpretation
