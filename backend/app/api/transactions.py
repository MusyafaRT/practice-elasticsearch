from fastapi import APIRouter, Query, HTTPException, status
from app.db.postgresql import AsyncSessionLocal
from app.services.transactions import TransactionsServices
from app.models.global_type import ResponseWrapper
from app.models.transactions import PaginatedTransactionItems
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.postgresql import get_db
from fastapi import Depends
from datetime import datetime


router = APIRouter(prefix='/transactions', tags=['transactions'])

@router.get('')
async def get_transactions(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(5, ge=1),
    search_query: str = Query(None),
    min_date: datetime = Query(None),
    max_date: datetime = Query(None),
):
    try:
        service = TransactionsServices(db)
        transactions= await service.get_transactions_data(
            session=db,
            page=page,
            page_size=page_size
        )

        return ResponseWrapper(
            status="success",
            message=f"Retrieved transaction items",
            data=transactions
        )
    except ConnectionError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Elasticsearch service is unavailable. Please check if the service is running."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

        
        
