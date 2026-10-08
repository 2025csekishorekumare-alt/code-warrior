from contextlib import asynccontextmanager
from fastapi import FastAPI,File,HTTPException,UploadFile
from .database import add_transaction,all_transactions,init_db
from .extraction import extract_text,parse_invoice
from .risk_engine import audit_invoice
from .schemas import TransactionIn
@asynccontextmanager
async def lifespan(app):init_db();yield
app=FastAPI(title="AP Audit Gateway",version="1.0.0",description="Automated invoice extraction, duplicate detection, anomaly analysis and AP risk scoring.",lifespan=lifespan)
@app.get("/health")
def health():return {"status":"ok","service":"ap-audit-gateway"}
@app.post("/transactions")
def create_transaction(transaction:TransactionIn):return add_transaction(transaction.model_dump())
@app.get("/transactions")
def get_transactions():return all_transactions()
@app.post("/invoices/audit")
async def audit_invoice_upload(file:UploadFile=File(...)):
    allowed={".pdf",".png",".jpg",".jpeg",".tiff",".bmp"}; filename=file.filename or "invoice"; suffix="."+filename.rsplit(".",1)[-1].lower() if "." in filename else ""
    if suffix not in allowed:raise HTTPException(status_code=400,detail="Unsupported file type.")
    data=await file.read()
    if len(data)>15*1024*1024:raise HTTPException(status_code=413,detail="File exceeds 15 MB limit.")
    try:
        text=extract_text(data,filename); invoice=parse_invoice(text); audit=audit_invoice(invoice)
        return {"filename":filename,"extracted":{"vendor":invoice.vendor,"invoice_number":invoice.invoice_number,"invoice_date":invoice.invoice_date,"subtotal":invoice.subtotal,"tax":invoice.tax,"total":invoice.total,"line_items":[i.__dict__ for i in invoice.line_items]},"audit":{"risk_score":audit.risk_score,"risk_level":audit.risk_level,"decision":audit.decision,"signals":audit.signals,"reasons":audit.reasons},"raw_text_preview":text[:2000]}
    except ValueError as exc:raise HTTPException(status_code=400,detail=str(exc))
    except Exception as exc:raise HTTPException(status_code=500,detail=f"Invoice processing failed: {exc}")
