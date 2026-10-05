from pathlib import Path
from fastapi import FastAPI,File,UploadFile,HTTPException,Form
from fastapi.responses import FileResponse,StreamingResponse
from app.services.pdf_ocr import extract_pages
from app.services.tender_parser import parse_tender,extract_requirements,detect_risks
from app.services.storage import init_db,save_tender,list_tenders,get_tender
from app.services.exporter import tender_xlsx
from app.services.addendum import compare_pages
from app.services.product_matcher import match_products
from app.services.compliance import build_compliance
from app.services.sync import sync_google_sheets,sync_firebase

app=FastAPI(title='TenderMate – IT Pre-Sales Assistant',version='1.0.0')
BASE=Path(__file__).resolve().parents[2]; FRONTEND=BASE/'frontend'
init_db()

@app.get('/')
def home(): return FileResponse(FRONTEND/'index.html')
@app.post('/api/sync/{tender_id}')
def sync(tender_id:int):
    p=get_tender(tender_id)
    if not p: raise HTTPException(404,'Tender not found')
    return {'google_sheets':sync_google_sheets(p),'firebase':sync_firebase(p)}

@app.get('/api/health')
def health(): return {'status':'ok','app':'TenderMate','version':'1.0.0'}

async def analyze_bytes(data,filename):
    pages=extract_pages(data); summary=parse_tender(pages); requirements=extract_requirements(pages)
    return {'filename':filename,'page_count':len(pages),'summary':summary.model_dump(),'requirements':[x.model_dump() for x in requirements],'risks':detect_risks(summary,pages),'pages':pages}

@app.post('/api/analyze')
async def analyze(file:UploadFile=File(...)):
    if not file.filename.lower().endswith('.pdf'): raise HTTPException(400,'Please upload a PDF file.')
    data=await file.read()
    if not data: raise HTTPException(400,'The uploaded PDF is empty.')
    if len(data)>100*1024*1024: raise HTTPException(413,'PDF is larger than 100 MB.')
    try:return await analyze_bytes(data,file.filename)
    except Exception as e: raise HTTPException(500,f'Unable to process PDF: {e}')

@app.post('/api/tenders')
async def create_tender(file:UploadFile=File(...)):
    payload=await analyze_bytes(await file.read(),file.filename)
    payload['id']=save_tender(payload); return payload

@app.get('/api/tenders')
def tenders(): return list_tenders()
@app.get('/api/tenders/{tender_id}')
def tender(tender_id:int):
    p=get_tender(tender_id)
    if not p: raise HTTPException(404,'Tender not found')
    return p

@app.post('/api/export')
async def export(file:UploadFile=File(...)):
    p=await analyze_bytes(await file.read(),file.filename); out=tender_xlsx(p)
    return StreamingResponse(out,media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',headers={'Content-Disposition':f'attachment; filename="{Path(file.filename).stem}_TenderMate.xlsx"'})

@app.post('/api/compare-addendum')
async def compare(old_file:UploadFile=File(...),new_file:UploadFile=File(...)):
    old=extract_pages(await old_file.read()); new=extract_pages(await new_file.read())
    return {'old_pages':len(old),'new_pages':len(new),'changes':compare_pages(old,new)}

@app.post('/api/product-match')
async def product_match(file:UploadFile=File(...)):
    p=await analyze_bytes(await file.read(),file.filename)
    text='\n'.join(x['text'] for x in p['pages']); return {'matches':match_products(text),'filename':file.filename}

@app.post('/api/compliance')
async def compliance(file:UploadFile=File(...),offered_text:str=Form('')):
    p=await analyze_bytes(await file.read(),file.filename)
    return {'items':build_compliance(p['requirements'],offered_text),'requirements':p['requirements']}
