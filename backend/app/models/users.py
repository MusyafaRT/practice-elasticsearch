from pydantic import BaseModel, EmailStr, UUID4, ConfigDict
from typing import Optional

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str

class UserRead(BaseModel):
    id: UUID4
    first_name: str
    last_name: str
    email: EmailStr
    oauth_provider: Optional[str] = None
    profile_picture: Optional[str] = None
    is_oauth_user: bool = False

    model_config = ConfigDict(from_attributes=True)
    
class UserLogin(BaseModel):
    email: EmailStr
    password: str
    
class UserLoginRes(BaseModel):
    
     user_data: UserRead
     access_token: str
     refresh_token: str
     
     model_config = ConfigDict(from_attributes=True)
     
class OauthUserCreate(BaseModel):
    email: str
    first_name: str
    last_name: str
    oauth_provider: str
    oauth_id: str
    profile_picture: Optional[str] = None
    
    