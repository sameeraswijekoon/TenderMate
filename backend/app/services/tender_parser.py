import re
from app.models.tender import TenderField, TenderSummary

DATE = r"(?:\d{1,2}[./-]\d{1,2}[./-]\d{2,4}|\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})"

def find_field(pages, patterns, confidence=0.88):
    for page in pages:
        for pattern in patterns:
            match = re.search(pattern, page["text"], re.I | re.M)
            if match:
                value = match.group(1).strip(" :-.,;")
                return TenderField(value=value, page=page["page"], confidence=confidence)
    return TenderField()

def parse_tender(pages):
    all_text = "\n".join(p["text"] for p in pages)

    summary = TenderSummary(
        tender_title=find_field(pages, [
            rf"(?:tender|procurement)\s+(?:title|name)\s*[:\-]\s*(.+)",
            r"(?:subject of (?:the )?tender|description)\s*[:\-]\s*(.+)"
        ]),
        reference_number=find_field(pages, [
            r"(?:tender|procurement)\s*(?:no\.?|number|reference)\s*[:#\-]\s*([A-Z0-9./_-]+)"
        ]),
        closing_date=find_field(pages, [
            rf"(?:closing|submission)\s+(?:date|deadline)\s*[:\-]?\s*({DATE})"
        ]),
        closing_time=find_field(pages, [
            r"(?:closing|submission)\s+(?:time|deadline)\s*[:\-]?\s*([0-9]{1,2}[:.]?[0-9]{2}\s*(?:AM|PM)?)"
        ]),
        pre_bid_date=find_field(pages, [
            rf"(?:pre[- ]bid|prebid)\s+(?:meeting\s+)?date\s*[:\-]?\s*({DATE})"
        ]),
        pre_bid_time=find_field(pages, [
            r"(?:pre[- ]bid|prebid)(?: meeting)?\s+time\s*[:\-]?\s*([0-9]{1,2}[:.]?[0-9]{2}\s*(?:AM|PM)?)"
        ]),
        pre_bid_location=find_field(pages, [
            r"(?:pre[- ]bid|prebid)(?: meeting)?\s+(?:location|venue)\s*[:\-]\s*(.+)"
        ]),
        submission_location=find_field(pages, [
            r"(?:submission|bid)\s+(?:address|location|venue)\s*[:\-]\s*(.+)"
        ]),
        delivery_period=find_field(pages, [
            r"(?:delivery|completion)\s+(?:period|time)\s*[:\-]\s*(.+)"
        ]),
        bid_validity=find_field(pages, [
            r"(?:bid|offer|quotation)\s+validity\s*(?:period)?\s*[:\-]?\s*(.+)"
        ]),
        quantity=find_field(pages, [
            r"(?:quantity|qty\.?|number of (?:units|items))\s*[:\-]?\s*([0-9][0-9,]*)"
        ]),
        warranty=find_field(pages, [
            r"(?:warranty|guarantee)\s*(?:period)?\s*[:\-]?\s*(.+)"
        ]),
        bid_security=find_field(pages, [
            r"(?:bid|tender)\s+security\s*(?:amount|value|of)?\s*[:\-]?\s*(.+)"
        ]),
        performance_security=find_field(pages, [
            r"performance\s+security\s*(?:amount|value|of)?\s*[:\-]?\s*(.+)"
        ]),
        required_documents=find_field(pages, [
            r"(?:required|mandatory)\s+(?:documents|certificates)\s*[:\-]\s*(.+)"
        ]),
    )

    # Lightweight fallback: detect likely tender title from first page.
    if not summary.tender_title.value and pages:
        lines = [x.strip() for x in pages[0]["text"].splitlines() if x.strip()]
        for line in lines[:15]:
            if len(line) > 12 and "tender" in line.lower():
                summary.tender_title = TenderField(value=line, page=1, confidence=0.55)
                break

    return summary
