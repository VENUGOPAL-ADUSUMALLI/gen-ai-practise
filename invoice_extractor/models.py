from datetime import  date
from  pydantic import  BaseModel
class LineItem(BaseModel):
    description: str
    quantity : int
    unit_price : float
    amount : float


class Invoice(BaseModel):
    vendor : str
    date: date
    line_items : list[LineItem]
    total: float
    currency: str | None = None