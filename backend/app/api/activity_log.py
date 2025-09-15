from fastapi import APIRouter, Query
from app.services.activity_log import get_logs

router = APIRouter(prefix="/logs", tags=["Logs"])

@router.get("")
def fetch_logs(limit: int = Query(10, ge=1, le=100)):
    return get_logs(limit)
