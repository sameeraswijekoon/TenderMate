import io,re,fitz,pytesseract
from PIL import Image
def extract_pages(pdf_bytes):
 doc=fitz.open(stream=pdf_bytes,filetype='pdf');pages=[]
 for n,p in enumerate(doc,1):
  native=p.get_text('text').strip()
  if len(re.sub(r'\s+','',native))<40:
   pix=p.get_pixmap(matrix=fitz.Matrix(2.2,2.2),alpha=False);img=Image.open(io.BytesIO(pix.tobytes('png')));text=pytesseract.image_to_string(img,lang='eng',config='--psm 6').strip();method='ocr'
  else:text=native;method='text'
  pages.append({'page':n,'text':text,'method':method})
 doc.close();return pages
