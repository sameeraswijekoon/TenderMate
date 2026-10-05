import re
from app.models.tender import TenderField,TenderSummary,Requirement
DATE=r"(?:\d{1,2}[./-]\d{1,2}[./-]\d{2,4}|\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})"
def find_field(pages,patterns,confidence=.88):
    for p in pages:
        for pat in patterns:
            m=re.search(pat,p['text'],re.I|re.M)
            if m:
                v=re.sub(r'\s+',' ',m.group(1)).strip(' :-.,;')
                if v:return TenderField(value=v,page=p['page'],confidence=confidence)
    return TenderField()
def parse_tender(pages):
    s=TenderSummary(
      tender_title=find_field(pages,[r'(?:tender|procurement)\s+(?:title|name)\s*[:\-]\s*(.+)',r'(?:subject of (?:the )?tender|description)\s*[:\-]\s*(.+)']),
      reference_number=find_field(pages,[r'(?:tender|procurement)\s*(?:no\.?|number|reference)\s*[:#\-]\s*([A-Z0-9./_-]+)']),
      closing_date=find_field(pages,[rf'(?:closing|submission)\s+(?:date|deadline)\s*[:\-]?\s*({DATE})']),closing_time=find_field(pages,[r'(?:closing|submission)\s+(?:time|deadline)\s*[:\-]?\s*([0-9]{1,2}[:.]?[0-9]{2}\s*(?:AM|PM)?)']),
      pre_bid_date=find_field(pages,[rf'(?:pre[- ]bid|prebid)\s+(?:meeting\s+)?date\s*[:\-]?\s*({DATE})']),pre_bid_time=find_field(pages,[r'(?:pre[- ]bid|prebid)(?: meeting)?\s+time\s*[:\-]?\s*([0-9]{1,2}[:.]?[0-9]{2}\s*(?:AM|PM)?)']),pre_bid_location=find_field(pages,[r'(?:pre[- ]bid|prebid)(?: meeting)?\s+(?:location|venue)\s*[:\-]\s*(.+)']),submission_location=find_field(pages,[r'(?:submission|bid)\s+(?:address|location|venue)\s*[:\-]\s*(.+)']),delivery_period=find_field(pages,[r'(?:delivery|completion)\s+(?:period|time)\s*[:\-]?\s*(.+)']),bid_validity=find_field(pages,[r'(?:bid|offer|quotation)\s+validity\s*(?:period)?\s*[:\-]?\s*(.+)']),quantity=find_field(pages,[r'(?:quantity|qty\.?|number of (?:units|items))\s*[:\-]?\s*([0-9][0-9,]*)']),warranty=find_field(pages,[r'(?:warranty|guarantee)\s*(?:period)?\s*[:\-]?\s*(.+)']),bid_security=find_field(pages,[r'(?:bid|tender)\s+security\s*(?:amount|value|of)?\s*[:\-]?\s*(.+)']),performance_security=find_field(pages,[r'performance\s+security\s*(?:amount|value|of)?\s*[:\-]?\s*(.+)']),required_documents=find_field(pages,[r'(?:required|mandatory)\s+(?:documents|certificates)\s*[:\-]\s*(.+)']))
    if not s.tender_title.value and pages:
        for line in [x.strip() for x in pages[0]['text'].splitlines() if x.strip()][:20]:
            if len(line)>12 and any(k in line.lower() for k in ['tender','procurement','supply']): s.tender_title=TenderField(value=line,page=1,confidence=.55);break
    return s
def extract_requirements(pages):
    keys={'certificate':'Certificates','certification':'Certificates','security':'Security','document':'Documents','eligibility':'Eligibility','experience':'Eligibility','delivery':'Delivery','specification':'Technical','warranty':'Warranty'};out=[];seen=set()
    for p in pages:
      for raw in p['text'].splitlines():
        line=re.sub(r'\s+',' ',raw).strip(' •\t'); low=line.lower()
        if 12<=len(line)<=350:
          for k,c in keys.items():
            if k in low and (':' in line or any(x in low for x in ['required','shall','must','minimum','should'])):
              if low not in seen: seen.add(low);out.append(Requirement(category=c,requirement=line,page=p['page'],confidence=.72))
              break
    return out[:200]
def detect_risks(s,pages):
    risks=[]
    for n,f in [('Closing date',s.closing_date),('Closing time',s.closing_time),('Bid validity',s.bid_validity),('Warranty',s.warranty),('Delivery period',s.delivery_period),('Bid security',s.bid_security)]:
      if not f.value: risks.append(f'Could not confidently extract {n}. Verify manually.')
    if any(p['method']=='ocr' for p in pages): risks.append('Scanned pages detected. Verify OCR-sensitive dates, amounts and model numbers.')
    return risks
