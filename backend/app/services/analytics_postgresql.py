import logging
from typing import List
from datetime import datetime, timedelta
from sqlalchemy import select, desc, asc, case
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from sqlalchemy import func
from app.db.schemas import Transaction, TransactionItem, Product, ProductCategory, Customer
from app.models.global_type import ResponseWrapper
from app.models.sales import SalesTrendModel, ProductCategorySalesModel, ProductTopSoldSalesModel, CustomerAgeSpendingModel, CustomerAgeGroupModel, PeriodSummaryModel, SummaryModel



logger = logging.getLogger(__name__)

class AnalyticsPostgreSQL:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    def calc_growth(self, current, previous):
        if not previous or previous == 0:
            return None  
        return ((current - previous) / previous) * 100
        
    async def get_period_summary_data(self, start_date: datetime, end_date: datetime) -> ResponseWrapper[PeriodSummaryModel]:
        period_length = (end_date - start_date).days + 1
        prev_start_date = start_date - timedelta(days=period_length)
        prev_end_date = start_date - timedelta(days=1)
        
        
        current_sales_query = (
            select(func.sum(TransactionItem.quantity))
            .join(Transaction)
            .where(Transaction.transaction_date.between(start_date, end_date))
        )
        prev_sales_query = (
            select(func.sum(TransactionItem.quantity))
            .join(Transaction)
            .where(Transaction.transaction_date.between(prev_start_date, prev_end_date))
        )
        current_orders_query = (
            select(func.count(Transaction.id))
            .where(Transaction.transaction_date.between(start_date, end_date))
        )
        prev_orders_query = (
            select(func.count(Transaction.id))
            .where(Transaction.transaction_date.between(prev_start_date, prev_end_date))
        )
        
        current_revenue_query = (
            select(func.sum(Transaction.total_amount))
            .where(Transaction.transaction_date.between(start_date, end_date))
        )
        prev_revenue_query = (
            select(func.sum(Transaction.total_amount))
            .where(Transaction.transaction_date.between(prev_start_date, prev_end_date))
        )
        
        current_aov_query = (
            select(func.avg(Transaction.total_amount))
            .where(Transaction.transaction_date.between(start_date, end_date))
        )
        prev_aov_query = (
            select(func.avg(Transaction.total_amount))
            .where(Transaction.transaction_date.between(prev_start_date, prev_end_date))
        )

        try:
            async with self.db as session:
                current_sales = await session.execute(current_sales_query)
                current_sales_value = current_sales.scalar() or 0

                previous_sales = await session.execute(prev_sales_query)
                previous_sales_value = previous_sales.scalar() or 0

                current_orders = await session.execute(current_orders_query)
                current_orders_value = current_orders.scalar() or 0

                previous_orders = await session.execute(prev_orders_query)
                previous_orders_value = previous_orders.scalar() or 0

                current_revenue = await session.execute(current_revenue_query)
                current_revenue_value = current_revenue.scalar() or 0

                previous_revenue = await session.execute(prev_revenue_query)
                previous_revenue_value = previous_revenue.scalar() or 0

                current_aov = await session.execute(current_aov_query)
                current_aov_value = current_aov.scalar() or 0

                previous_aov = await session.execute(prev_aov_query)
                previous_aov_value = previous_aov.scalar() or 0

                # Growth
                sales_growth = self.calc_growth(current_sales_value, previous_sales_value)
                orders_growth = self.calc_growth(current_orders_value, previous_orders_value)
                revenue_growth = self.calc_growth(current_revenue_value, previous_revenue_value)
                aov_growth = self.calc_growth(current_aov_value, previous_aov_value)

                return ResponseWrapper[PeriodSummaryModel](
                    status="success",
                    message="Successfully retrieved period summary data",
                    data=PeriodSummaryModel(
                        sales_summary=SummaryModel(
                            summary_title="Products Sold",
                            current_period=current_sales_value,
                            previous_period=previous_sales_value,
                            growth=round(sales_growth, 2) if sales_growth is not None else None
                        ),
                        orders_summary=SummaryModel(
                            summary_title="Orders",
                            current_period=current_orders_value,
                            previous_period=previous_orders_value,
                            growth=round(orders_growth, 2) if orders_growth is not None else None
                        ),
                        revenue_summary=SummaryModel(
                            summary_title="Revenue",
                            current_period=round(float(current_revenue_value), 2),
                            previous_period=round(float(previous_revenue_value), 2),
                            growth=round(revenue_growth, 2) if revenue_growth is not None else None
                        ),
                        aov_summary=SummaryModel(
                            summary_title="Average Order Value",
                            current_period=round(float(current_aov_value), 2),
                            previous_period=round(float(previous_aov_value), 2),
                            growth=round(aov_growth, 2) if aov_growth is not None else None
                        ),
                    )
                )
        except Exception as e:
            logger.error(f"Error in get_period_summary_data: {str(e)}")
            raise
        finally:
            await self.db.close()


        
    async def get_sales_trend_data(
        self, start_date: datetime, end_date: datetime
    ) -> ResponseWrapper[List[SalesTrendModel]]:
        main_query = (
            select(
                Transaction.transaction_date,
                func.sum(Transaction.total_amount).label("total_sales"),
                func.count(Transaction.id).label("transaction_count"),
            ).where(
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date,
            ).group_by(
                Transaction.transaction_date
            ).order_by(
                asc(Transaction.transaction_date)
            )
        )

        try:
            async with self.db as session:
                result = await session.execute(main_query)
                rows = result.mappings().all()

                data: List[SalesTrendModel] = []
                for row in rows:
                    data.append(
                        SalesTrendModel(
                            transaction_date=row["transaction_date"].strftime("%Y-%m-%d"),
                            total_sales=float(row["total_sales"]) if row["total_sales"] else 0.0,
                            total_transactions=int(row["transaction_count"]) if row["transaction_count"] else 0
                        )
                    )

                return ResponseWrapper[List[SalesTrendModel]](
                    status="success",
                    message="Successfully retrieved sales_rows trend data",
                    data=data,
                )
        except Exception as e:
            logger.error(f"Error in get_sales_trend_data: {str(e)}")
            return ResponseWrapper[List[SalesTrendModel]](
                status="error",
                message=f"Error: {str(e)}",
                data=[],
            )
        finally:
            await self.db.close()
    
    async def get_category_sales_data(self, start_date: datetime, end_date: datetime) -> List[ProductCategorySalesModel] :
        main_query = (
            select(
                ProductCategory.id,
                ProductCategory.name.label("category_name"),
                func.sum(TransactionItem.quantity).label("total_quantity"),
                func.sum(TransactionItem.subtotal).label("total_sales"),
            )
            .join(Product, ProductCategory.id == Product.category_id)
            .join(TransactionItem, Product.id == TransactionItem.product_id)
            .join(Transaction, TransactionItem.transaction_id == Transaction.id)
            .where(
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date,
            )
            .group_by(ProductCategory.id, ProductCategory.name)
            .order_by(desc("total_sales"))
        )
        
        try:
            async with self.db as session:
                result = await session.execute(main_query)
                rows = result.mappings().all()
                
                data: List[ProductCategorySalesModel]  = []
                for row in rows:
                    data.append(ProductCategorySalesModel(
                        category_name=row["category_name"],
                        total_quantity=int(row["total_quantity"]) if row["total_quantity"] else 0, 
                        total_sales=float(row["total_sales"]) if row["total_sales"] else 0.0
                    ))
                
            return data

        except Exception as e:
            logger.error(f"Error in get_product_per_category_data: {str(e)}")
            raise
    
    async def get_product_top_sold_data(self, start_date: datetime, end_date: datetime) -> List[ProductTopSoldSalesModel] :
        main_query = select(
            Product.name.label("product_name"),
            func.sum(TransactionItem.quantity).label("total_quantity"),
            func.sum(TransactionItem.subtotal).label("total_sales")
        ).join(
            TransactionItem, Product.id == TransactionItem.product_id
        ).join(
            Transaction, TransactionItem.transaction_id == Transaction.id
        ).where(
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date
        ).group_by(
            Product.name
        ).order_by(
            desc("total_quantity")
        ).limit(5)
        
        try:
            async with self.db as session:
                result = await session.execute(main_query)
                rows = result.mappings().all()
                
                data: List[ProductTopSoldSalesModel]  = []
                for row in rows:
                    data.append(ProductTopSoldSalesModel(
                        product_name=row["product_name"],
                        total_quantity=int(row["total_quantity"]) if row["total_quantity"] else 0, 
                        total_sales=float(row["total_sales"]) if row["total_sales"] else 0.0
                    ))
                
            return data

        except Exception as e:
            logger.error(f"Error in get_product_per_category_data: {str(e)}")
            raise
    
    async def get_product_analytics_data(self, start_date: datetime, end_date: datetime):
        try:
            category_sales = await self.get_category_sales_data(start_date, end_date)
            top_sold_products = await self.get_product_top_sold_data(start_date, end_date)

            return ResponseWrapper[dict](
                status="success",
                message="Successfully retrieved product analytics data",
                data={
                    "category_sales": category_sales,
                    "top_sold_products": top_sold_products,
                }
            )

        except Exception as e:
            logger.error(f"Error in get_product_analytics_data: {str(e)}")
            raise

    async def customers_age_spending_data(self, start_date: datetime, end_date: datetime):
        main_query = select(
            Customer.age,
            func.sum(Transaction.total_amount).label("total_spending"),
            func.count(Transaction.id).label("transaction_count")
        ).join(
            Transaction, Customer.id == Transaction.customer_id
        ).where(
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date
        ).group_by(
            Customer.age
        ).order_by(
            asc(Customer.age)
        )
        
        try:
            async with self.db as session:
                result = await session.execute(main_query)
                rows = result.mappings().all()
                
                data: List[CustomerAgeSpendingModel]  = []
                for row in rows:
                    data.append(CustomerAgeSpendingModel(
                        age=row["age"],
                        total_spending=float(row["total_spending"]) if row["total_spending"] else 0.0,
                        transaction_count=int(row["transaction_count"]) if row["transaction_count"] else 0
                    ))
                
            return data

        except Exception as e:
            logger.error(f"Error in get_product_per_category_data: {str(e)}")
            raise
    
    async def customers_age_group_data(self, start_date: datetime, end_date: datetime):
        age_group_cte = select(
            Customer.id.label("customer_id"),
            case(
                (Customer.age.between(18, 24), "18-24"),
                (Customer.age.between(25, 34), "25-34"),
                (Customer.age.between(35, 44), "35-44"),
                (Customer.age.between(45, 54), "45-54"),
                (Customer.age >= 55, "55+")
            ).label("age_group")
        )
        
        main_query = select(
            age_group_cte.c.age_group,
            ProductCategory.name.label("category"),
            func.sum(TransactionItem.subtotal).label("total_sales"),
        ).join(
            Transaction, age_group_cte.c.customer_id == Transaction.customer_id
        ).join(
            TransactionItem, Transaction.id == TransactionItem.transaction_id
        ).join(
            Product, TransactionItem.product_id == Product.id
        ).join(
            ProductCategory, Product.category_id == ProductCategory.id
        ).where(
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date
        ).group_by(
            age_group_cte.c.age_group, ProductCategory.name
        ).order_by(
            asc(age_group_cte.c.age_group), desc("total_sales") 
        )
        
        try:
            async with self.db as session:
                result = await session.execute(main_query)
                rows = result.mappings().all()
                
                data: List[CustomerAgeGroupModel]  = []
                for row in rows:
                    data.append(CustomerAgeGroupModel(
                        age_group=row["age_group"],
                        category=row["category"],
                        total_sales=float(row["total_sales"]) if row["total_sales"] else 0.0
                    ))
                
            return data

        except Exception as e:
            logger.error(f"Error in get_product_per_category_data: {str(e)}")
            raise
    
    async def get_customers_analytics_data(self, start_date: datetime, end_date: datetime):
        try:
            age_spending = await self.customers_age_spending_data(start_date, end_date)
            age_group = await self.customers_age_group_data(start_date, end_date)
            
            return ResponseWrapper[dict](
                status="success",
                message="Successfully retrieved customers analytics data",
                data={
                    "age_spending": age_spending,
                    "age_group": age_group,
                }
            )
        
        except Exception as e:
            logger.error(f"Error in get_customers_analytics_data: {str(e)}")
            raise
            