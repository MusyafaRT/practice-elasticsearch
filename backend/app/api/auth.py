from fastapi import APIRouter, Depends, Query, HTTPException, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.postgresql import get_db
from app.models.users import UserCreate, UserRead, UserLogin, UserLoginRes
from app.models.global_type import ResponseWrapper
import app.services.auth as user_service
from app.services.activity_log import log_activity, ActionEnum

router = APIRouter(prefix="/auth", tags=["Users"])


@router.get("/oauth/{provider}/login")
async def oauth_login(
    provider: str,
    db: AsyncSession = Depends(get_db)  # kalau butuh DB
):
    return await user_service.initiate_oauth_login(provider)


@router.get("/oauth/{provider}/callback")
async def oauth_callback(provider:str, code:str = Query(...), state:str = Query(...), db: AsyncSession = Depends(get_db)):
    if provider not in ["google"]:
        raise HTTPException(status_code=400, detail="Unsupported OAuth Provider")
    
    response = await user_service.handle_oauth_callback(db, provider, code, state)
    
    return response
    
    
@router.post("/register", response_model=ResponseWrapper[UserRead])
async def user_register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    log_activity(
        action=ActionEnum.CREATE,
        details={"email_user": user.email, "first_name": user.first_name, "last_name": user.last_name}
    )
    return await user_service.register_user(db, user)

@router.post("/login", response_model=ResponseWrapper[UserLoginRes])
async def user_login(user: UserLogin, response: Response , db: AsyncSession = Depends(get_db)):
    result = await user_service.login_user(response, db, user)
    if not result.data:  
        return result
    log_activity(
        user_id=result.data.user_data.id,
        last_name=result.data.user_data.last_name,
        action=ActionEnum.CREATE,
        details={"email_user": user.email}
    )
    return result

@router.post("/refresh-token", response_model=ResponseWrapper[dict])
async def refresh_token(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    return await user_service.refresh_token(request, response, db)


