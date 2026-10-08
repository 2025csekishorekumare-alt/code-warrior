from dataclasses import dataclass, field
from typing import List, Optional
@dataclass
class LineItem:
    description: str
    quantity: float=1.0
    unit_price: float=0.0
    total: float=0.0
@dataclass
class Invoice:
    vendor: str="Unknown Vendor"
    invoice_number: str="UNKNOWN"
    invoice_date: Optional[str]=None
    currency: str="USD"
    subtotal: float=0.0
    tax: float=0.0
    total: float=0.0
    line_items: List[LineItem]=field(default_factory=list)
@dataclass
class AuditResult:
    risk_score: int
    risk_level: str
    decision: str
    reasons: List[str]
    signals: dict
