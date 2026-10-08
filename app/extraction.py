import io,re
from pathlib import Path
from PIL import Image
from .config import OCR_ENABLED
from .models import Invoice,LineItem
def extract_text(data,filename):
    suffix=Path(filename).suffix.lower()
    if suffix==".pdf":
        import fitz; doc=fitz.open(stream=data,filetype="pdf"); return "\n".join(p.get_text() for p in doc)
    if suffix in {".png",".jpg",".jpeg",".tiff",".bmp"}:
        if not OCR_ENABLED:return ""
        try:
            import pytesseract; return pytesseract.image_to_string(Image.open(io.BytesIO(data)))
        except Exception:return ""
    raise ValueError("Unsupported file type. Use PDF, PNG, JPG, JPEG, TIFF, or BMP.")
def _money(value):return float(re.sub(r"[^0-9.\-]","",value).replace(",","") or 0)
def _first(patterns,text,default=""):
    for p in patterns:
        m=re.search(p,text,re.I|re.M)
        if m:return m.group(1).strip()
    return default
def parse_invoice(text):
    vendor=_first([r"^vendor\s*[:#-]\s*(.+)$",r"^supplier\s*[:#-]\s*(.+)$",r"^from\s*[:#-]\s*(.+)$"],text,"Unknown Vendor")
    number=_first([r"invoice\s*(?:number|no|#|id)?\s*[:#-]\s*([A-Z0-9][A-Z0-9\-/_.]+)",r"inv(?:oice)?\s*#\s*([A-Z0-9][A-Z0-9\-/_.]+)"],text,"UNKNOWN")
    date=_first([r"(?:invoice\s*)?date\s*[:#-]\s*([0-9]{1,4}[-/][0-9]{1,2}[-/][0-9]{1,4})"],text,None)
    total=_money(_first([r"(?:grand\s+total|invoice\s+total|total\s+due|amount\s+due|total)\s*[:#-]?\s*[$€£]?\s*([0-9,]+(?:\.\d{1,2})?)"],text,"0"))
    tax=_money(_first([r"tax\s*[:#-]?\s*[$€£]?\s*([0-9,]+(?:\.\d{1,2})?)"],text,"0"))
    subtotal=_money(_first([r"subtotal\s*[:#-]?\s*[$€£]?\s*([0-9,]+(?:\.\d{1,2})?)"],text,"0"))
    items=[]
    for line in text.splitlines():
        m=re.match(r"^\s*(.+?)\s*[|,]\s*([0-9]+(?:\.\d+)?)\s*[|,]\s*[$€£]?\s*([0-9,]+(?:\.\d+)?)\s*[|,]\s*[$€£]?\s*([0-9,]+(?:\.\d+)?)\s*$",line)
        if m:items.append(LineItem(m.group(1).strip(),float(m.group(2)),_money(m.group(3)),_money(m.group(4))))
    return Invoice(vendor=vendor,invoice_number=number,invoice_date=date,subtotal=subtotal,tax=tax,total=total,line_items=items)
