from pydantic import BaseModel
from typing import Optional
from decimal import Decimal

class SummaryModel(BaseModel):
    summary_title: str
    current_period: float | int | Decimal
    previous_period: float | int | Decimal
    growth: Optional[float]

    class Config:
        orm_mode = True
          
class PeriodSummaryModel(BaseModel):
    sales_summary: SummaryModel
    orders_summary: SummaryModel
    revenue_summary: SummaryModel
    aov_summary: SummaryModel

    class Config:
        orm_mode = True

class SalesTrendModel(BaseModel):
    transaction_date: str
    total_sales: float
    total_transactions: int

    class Config:
        orm_mode = True
        
class ProductCategorySalesModel(BaseModel):
    category_name: str
    total_quantity: int
    total_sales: float

    class Config:
        orm_mode = True

class ProductTopSoldSalesModel(BaseModel):
    product_name: str
    total_quantity: int
    total_sales: float

    class Config:
        orm_mode = True

class CustomerAgeSpendingModel(BaseModel):
    age: int
    total_spending: float
    transaction_count: int

    class Config:
        orm_mode = True
        
class CustomerAgeGroupModel(BaseModel):
    age_group: str
    category: str
    total_sales: float

    class Config:
        orm_mode = True