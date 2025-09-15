# app/main.py
from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from app.db.postgresql import engine
from app.db.schemas import Base
import app.api.auth as auth
import app.api.analytics as analytics
import app.api.activity_log as activity_log
import app.api.transactions as transactions
from fastapi.middleware.cors import CORSMiddleware
from app.db.elastic import get_es_client
from app.services.analytics_services import AnalyticsService
from app.services.transactions import TransactionsServices
from app.db.postgresql import AsyncSessionLocal
from app.dependencies import get_current_user
import asyncio
import logging

logger = logging.getLogger(__name__)
analytics_service = AnalyticsService()



@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting application...")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ PostgreSQL initialized")

    
    es = get_es_client()
    
    for i in range(5):
        if es.ping():
            break
        await asyncio.sleep(1)
    else:
        logger.warning("Elasticsearch is not reachable at startup!")
        
    if(es.ping()):
        async with AsyncSessionLocal() as db:
            transactions_service = TransactionsServices(db)
            # await analytics_service.ensure_all_indices_exist()
            # await transactions_service.ensure_all_indices_exist()
            # await analytics_service.sync_sales_analytics()
            # await transactions_service.sync_transactions_data_to_es()
            logger.info("✅ All indices ensured")
        print("✅ Elasticsearch initialized")
        
    yield   

    print("🛑 Shutting down application...")
    await engine.dispose()
    print("✅ PostgreSQL connection closed")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

app.include_router(auth.router)
app.include_router(activity_log.router)
app.include_router(analytics.router)
app.include_router(transactions.router, dependencies=[Depends(get_current_user)])
