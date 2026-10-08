from typing import Optional
from pydantic import BaseModel,Field
class TransactionIn(BaseModel):
    vendor:str
    invoice_number:str
    invoice_date:Optional[str]=None
    description:str=""
    quantity:float=Field(default=1,ge=0)
    unit_price:float=Field(default=0,ge=0)
    total:float=Field(default=0,ge=0)
    paid:int=Field(default=1,ge=0,le=1)
