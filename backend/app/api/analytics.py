from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.elastic import get_es_client
from app.db.postgresql import get_db
from app.services.analytics_services import AnalyticsService, get_sales_from_es, get_categories_from_es, get_customers_from_es, get_customers_age_group_from_es
from app.services.analytics_postgresql import AnalyticsPostgreSQL
from app.models.global_type import ResponseWrapper
from typing import Optional
from datetime import datetime, timedelta
from fastapi import Query
from app.services.news_analytics import NewsAnalyticsService


router = APIRouter(prefix="/analytics", tags=["Analytics"])
analytics_service = AnalyticsService()

@router.get("/news")
def analytics_overview( 
    search_query: Optional[str] = Query(None, description="Search query"),
    start_date: Optional[datetime] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[datetime] = Query(None, description="End date (YYYY-MM-DD)")
):
    analytics = NewsAnalyticsService()
    
    overview = analytics.get_overview(
        search_query=search_query,
        start_date=start_date,
        end_date=end_date
    )  
    
    return ResponseWrapper[dict](
        status="success",
        message="Successfully retrieved news analytics data",
        data=overview
    )

@router.get("/news/recent")
async def get_recent_news(
    size: int = Query(10, description="Number of news to retrieve"),
    start_date: Optional[datetime] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[datetime] = Query(None, description="End date (YYYY-MM-DD)"),
    search_query: Optional[str] = Query(None, description="Search query"),
    search_after: Optional[list] = Query(None, description="Search after")
): 
    analytics = NewsAnalyticsService()
    
    recent_news, next_search_after = analytics.get_recent_news(
        size=size,
        start_date=start_date,
        end_date=end_date,
        search_query=search_query,
        search_after=search_after
    )
    
    return ResponseWrapper[dict](
        status="success",
        message="Successfully retrieved recent news",
        data={
            "items": recent_news,
            "next_search_after": next_search_after
        }
    )


@router.get("/summary")
async def sales_summary(
    db: AsyncSession = Depends(get_db),
    start_date: Optional[datetime] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[datetime] = Query(None, description="End date (YYYY-MM-DD)"),
):
    try:
        analytics_service_pgsql = AnalyticsPostgreSQL(db)
        
        if not start_date:
            start_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=30)
        
        if not end_date:
            end_date = datetime.utcnow()
        
        data = await analytics_service_pgsql.get_period_summary_data(start_date, end_date)
        
        return data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
        


@router.get("/sales")
async def sales_analytics(
    sync_first: bool = True,
    db: AsyncSession = Depends(get_db)
):
    try:
        if sync_first:
            synced_count = await analytics_service.sync_sales_analytics()

        data = await get_sales_from_es()
        
        return ResponseWrapper[dict](
            status="success",
            message=f"Retrieved {len(data)} sales analytics records",
            data={
                "count": len(data),
                "items": data,
            }
        )
        
    except ConnectionError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Elasticsearch service is unavailable. Please check if the service is running."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
        
@router.get("/sales-pgsql")
async def sales_analytics_pgsql(
    start_date: Optional[datetime] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[datetime] = Query(None, description="End date (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db)
):
    try:
        analytics_service_pgsql = AnalyticsPostgreSQL(db)
        
        if not start_date:
            start_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=30)
        
        if not end_date:
            end_date = datetime.utcnow()
        
        data = await analytics_service_pgsql.get_sales_trend_data(start_date, end_date)
        
        return data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
        

@router.get("/products")
async def categories_sales_analytics_pgsql(
    start_date: Optional[datetime] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[datetime] = Query(None, description="End date (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db)
):
    try:
        analytics_service_pgsql = AnalyticsPostgreSQL(db)
        
        if not start_date:
            start_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=30)
        
        if not end_date:
            end_date = datetime.utcnow()
        
        data = await analytics_service_pgsql.get_product_analytics_data(start_date, end_date)
        
        return data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/customers")
async def get_customers_analytics(
    db: AsyncSession = Depends(get_db),
    start_date: Optional[datetime] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[datetime] = Query(None, description="End date (YYYY-MM-DD)"),
):
    try:
        analytics_service_pgsql = AnalyticsPostgreSQL(db)
        if not start_date:
            start_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=30)
        
        if not end_date:
            end_date = datetime.utcnow()
        
        data = await analytics_service_pgsql.get_customers_analytics_data(start_date, end_date)
        
        return data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
        



        
@router.get("/categories")
async def categories_analytics(
    sync_first: bool = True,
    db: AsyncSession = Depends(get_db)
):
    try:
        if sync_first:
            synced_count = await analytics_service.sync_categories_analytics()

        data = await get_categories_from_es()
        
        return ResponseWrapper[dict](
            status="success",
            message=f"Retrieved {len(data)} sales analytics records",
            data={
                "count": len(data),
                "items": data,
            }
        )
        
    except ConnectionError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Elasticsearch service is unavailable. Please check if the service is running."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
        
@router.get("/customers/age-group")
async def customers_age_group_analytics(
    sync_first: bool = True,
    db: AsyncSession = Depends(get_db)
):
    try:
        if sync_first:
            synced_count = await analytics_service.sync_customers_age_group_analytics()
        
        data = await get_customers_age_group_from_es()
        
        return ResponseWrapper[dict](
            status="success",
            message=f"Retrieved {len(data)} sales analytics records",
            data={
                "count": len(data),
                "items": data,
            }
        )
    
    except ConnectionError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
        
@router.get("/customers/gender")
async def customers_analytics(
    sync_first: bool = True,
    db: AsyncSession = Depends(get_db)
):
    try:
        if sync_first:
            synced_count = await analytics_service.sync_customers_analytics()
        
        data = await get_customers_from_es()
        
        return ResponseWrapper[dict](
            status="success",
            message=f"Retrieved {len(data)} sales analytics records",
            data={
                "count": len(data),
                "items": data,
            }
        )
    
    except ConnectionError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )