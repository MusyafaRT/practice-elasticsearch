from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.postgresql import get_db
from app.models.users import UserRead
from app.core.security import verify_token, SECRET_KEY, ALGORITHM
import app.services.auth as user_service
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

bearer_scheme = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    token = credentials.credentials
    payload = verify_token(token, SECRET_KEY, ALGORITHM)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id: str = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return UserRead.from_orm(user)
