from statistics import mean
from difflib import SequenceMatcher
from .database import find_invoice,vendor_prices,all_transactions
from .models import AuditResult
def _clamp(v):return max(0,min(100,int(round(v))))
def audit_invoice(invoice):
    reasons=[]; duplicate=price=vendor=quantity=payment=0
    if find_invoice(invoice.vendor,invoice.invoice_number): duplicate=100; reasons.append("Exact vendor + invoice number already exists in transaction history.")
    else:
        for row in all_transactions()[:500]:
            ratio=SequenceMatcher(None,invoice.invoice_number.lower(),str(row["invoice_number"]).lower()).ratio()
            if invoice.invoice_number!="UNKNOWN" and ratio>=.90:duplicate=75; reasons.append("Invoice number closely matches a historical invoice."); break
    observed=[]
    for item in invoice.line_items:observed.extend(vendor_prices(invoice.vendor,item.description))
    if observed:
        baseline=mean(observed); current=mean([i.unit_price for i in invoice.line_items if i.unit_price>0] or [0])
        if current and baseline:
            deviation=abs(current-baseline)/baseline; price=_clamp(deviation*180)
            if deviation>=.20:reasons.append("Average unit price is "+format(deviation,".0%")+" "+("above" if current>baseline else "below")+" historical vendor pricing.")
    if invoice.vendor.lower() in {"unknown vendor","","unknown"}:vendor=50; reasons.append("Vendor could not be confidently extracted.")
    elif len(invoice.vendor)<3:vendor=35; reasons.append("Vendor identity appears incomplete.")
    if invoice.line_items:
        bad=sum(1 for i in invoice.line_items if i.quantity<=0 or i.quantity>10000); quantity=_clamp(bad/len(invoice.line_items)*100)
        if quantity:reasons.append("One or more line-item quantities are unusual.")
    else:quantity=30; reasons.append("No structured line items were extracted.")
    if invoice.total<=0:payment=80; reasons.append("Invoice total is missing or zero.")
    elif invoice.line_items:
        computed=sum(i.total or i.quantity*i.unit_price for i in invoice.line_items); mismatch=abs(invoice.total-computed)/max(invoice.total,computed) if computed else 0; payment=_clamp(mismatch*200)
        if mismatch>=.10:reasons.append("Invoice total materially differs from extracted line-item totals.")
    score=_clamp(duplicate*.30+price*.25+vendor*.15+quantity*.15+payment*.15)
    if score<=30:level,decision="LOW","APPROVE"
    elif score<=60:level,decision="MEDIUM","REVIEW"
    elif score<=80:level,decision="HIGH","MANUAL_REVIEW"
    else:level,decision="CRITICAL","BLOCK"
    return AuditResult(score,level,decision,reasons or ["No material audit anomalies detected."],{"duplicate":duplicate,"price_anomaly":price,"vendor":vendor,"quantity_anomaly":quantity,"payment_anomaly":payment})
