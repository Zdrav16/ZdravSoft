from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List

class SaleItemBase(BaseModel):
    product_id: int
    quantity: int
    price: float

class SaleItemCreate(SaleItemBase):
    pass

class SaleItem(SaleItemBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class SaleBase(BaseModel):
    total_amount: float

class SaleCreate(SaleBase):
    items: List[SaleItemCreate]

class Sale(SaleBase):
    id: int
    date: datetime
    items: List[SaleItem]
    model_config = ConfigDict(from_attributes=True)
