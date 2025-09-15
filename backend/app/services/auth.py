from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from app.db.schemas import User
from app.models.users import UserCreate, UserLogin, UserRead, UserLoginRes, OauthUserCreate
import secrets
from fastapi import HTTPException, Response, Request
from fastapi.responses import JSONResponse, RedirectResponse
from app.models.global_type import ResponseWrapper 
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
from app.core.redis_utils import store_refresh_token, store_oauth_state, get_oauth_state, delete_oauth_state, redis_client, revoke_refresh_token
from app.services.oauth_client import OAuthClient
from app.core.config import OAUTH_PROVIDERS

async def initiate_oauth_login(provider:str):
    try:
        oauth_client = OAuthClient(provider=provider)
        state = secrets.token_urlsafe(32)
        
        await store_oauth_state(state=state, provider=provider, expire_seconds=600)
        
        authorization_url = oauth_client.get_authorization_url(state)
        
        return ResponseWrapper[dict](
            status="success",
            message=f"{provider.capitalize()} OAuth initiated",
            data={
                "authorization_url": authorization_url,
                "state": state
            }
        )
    except Exception as e:
        return JSONResponse(
        status_code=400,
        content=ResponseWrapper[dict](
            status="error",
            message=f"Failed to initiate OAuth: {e}"
        ).dict()
    )
        
        
async def handle_oauth_callback(
    db: AsyncSession,
    provider: str, 
    code: str,
    state: str,
): 
    try:
        stored_provider = await get_oauth_state(state=state)  
        
        if not stored_provider or stored_provider != provider:
            raise HTTPException(status_code=400, detail="Invalid state parameter")
        
        await delete_oauth_state(state=state)
        
        oauth_client = OAuthClient(provider)
        
        token_data = await oauth_client.exchange_code_for_token(code)
        if not token_data:
            raise HTTPException(status_code=400, detail="Failed to exchange code for token")
        
        access_token = token_data.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="No access token received")
            
        user_info = await oauth_client.get_user_info(access_token)
        
        if not user_info:
            raise HTTPException(status_code=400, detail="Failed to fetch user information")
        
        if not user_info.get("email"):
            raise HTTPException(status_code=400, detail="Email not provided by OAuth provider")
        
        result = await db.execute(select(User).where(User.email == user_info["email"]))
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            is_already_oauth = bool(existing_user.is_oauth_user) if existing_user.is_oauth_user is not None else False
            
            if not is_already_oauth:
                update_stmt = (
                    update(User)
                    .where(User.id == existing_user.id)
                    .values(
                        oauth_provider=user_info["provider"],
                        oauth_id=user_info["id"],
                        is_oauth_user=True,
                        profile_picture=user_info.get("picture")
                    )
                )
                await db.execute(update_stmt)
                await db.commit()
                
                await db.refresh(existing_user)
            
            user = existing_user
        else:
            oauth_user_data = OauthUserCreate(
                email=user_info["email"],
                first_name=user_info.get("first_name", ""),
                last_name=user_info.get("last_name", ""),
                oauth_provider=user_info["provider"],
                oauth_id=str(user_info["id"]),
                profile_picture=user_info.get("picture")
            )
            
            new_user = User(
                email=oauth_user_data.email,
                first_name=oauth_user_data.first_name,
                last_name=oauth_user_data.last_name,
                oauth_provider=oauth_user_data.oauth_provider,
                oauth_id=oauth_user_data.oauth_id,
                profile_picture=oauth_user_data.profile_picture,
                is_oauth_user=True,
                password_hash="OAUTH_USER"  
            )
            
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            user = new_user
        
        jwt_access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})
        await store_refresh_token(str(user.id), refresh_token)
        return RedirectResponse(
            f"http://localhost:5173/oauth-callback?access_token={jwt_access_token}&refresh_token={refresh_token}"
        )
        
       
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OAuth callback failed: {str(e)}")


async def register_user(db: AsyncSession, user: UserCreate):
    result = await db.execute(select(User).where(User.email == user.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        return ResponseWrapper[UserRead](
            status="error",
            message="Email already registered",
            data=None
        )
    
    password_hash = hash_password(user.password) 
    new_user = User(
        password_hash=password_hash,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return ResponseWrapper[UserRead](
        status="success",
        message="User registered successfully",
        data=UserRead.from_orm(new_user)
    )

async def login_user(response: Response, db: AsyncSession, user: UserLogin):
    result = await db.execute(select(User).where(User.email == user.email))
    db_user = result.scalar_one_or_none()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(user.password, str(db_user.password_hash)):
        raise HTTPException(status_code=401, detail="Invalid password")
    
    access_token = create_access_token({"sub": str(db_user.id)})
    refresh_token = create_refresh_token({"sub": str(db_user.id)})
    await store_refresh_token(str(db_user.id), refresh_token)
    
    user_response = UserLoginRes(
        user_data=UserRead.from_orm(db_user),
        access_token=access_token,
        refresh_token=refresh_token
    )
    
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,         
        samesite="lax",        
        max_age=60*15  
    )
    
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 7, 
    )

    return ResponseWrapper[UserLoginRes](
        status="success",
        message="User Login successfully",
        data=user_response
    )
    
async def refresh_token(request: Request, response: Response, db: AsyncSession):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token not found")

    user_id = await redis_client.get(f"refresh_token:{refresh_token}")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    user_id = user_id.decode() if isinstance(user_id, bytes) else str(user_id)

    result = await db.execute(select(User).where(User.id == user_id))
    db_user = result.scalar_one_or_none()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    new_access_token = create_access_token({"sub": str(db_user.id)})
    new_refresh_token = create_refresh_token({"sub": str(db_user.id)})

    await revoke_refresh_token(refresh_token)
    await store_refresh_token(user_id, new_refresh_token)

    response.set_cookie("access_token", new_access_token, httponly=True, max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    response.set_cookie("refresh_token", new_refresh_token, httponly=True, max_age=REFRESH_TOKEN_EXPIRE_DAYS * 86400)

    return ResponseWrapper[dict](
        status="success",
        message="Token refreshed successfully",
        data={"access_token": new_access_token, "refresh_token": new_refresh_token}
    )

async def get_users(db: AsyncSession):
    result = await db.execute(select(User))
    return result.scalars().all()

async def get_user_by_id(db: AsyncSession, user_id: str):
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()
