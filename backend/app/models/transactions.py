from pydantic import BaseModel, ConfigDict
from app.models.global_type import PaginationMetaData
from datetime import date
from sqlalchemy import Date



class TransactionItemModel(BaseModel):
    transaction_id: str
    transaction_date: date  
    customer_name: str
    gender: str | None = None
    age: int | None = None
    products_name: str
    total_amount: float
    
    model_config = ConfigDict(from_attributes=True)
    

class PaginatedTransactionItems(BaseModel):
    items: list[TransactionItemModel]
    metadata: PaginationMetaData


