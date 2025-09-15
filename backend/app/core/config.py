# app/config.py
from pydantic_settings import BaseSettings
from typing import Dict, Any

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://ecommerce:Niffier2025@localhost:5433/ecommerce"

    class Config:
        extra = "ignore"
        env_file = ".env"

settings = Settings()

class OAuthSettings(BaseSettings):
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/auth/oauth/google/callback"

    class Config:
        extra = "ignore"
        env_file = ".env"

oauth_settings = OAuthSettings()

OAUTH_PROVIDERS = {
    "google": {
        "authorization_url": "https://accounts.google.com/o/oauth2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "user_info_url": "https://openidconnect.googleapis.com/v1/userinfo",
        "client_id": oauth_settings.GOOGLE_CLIENT_ID,
        "client_secret": oauth_settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": oauth_settings.GOOGLE_REDIRECT_URI,
        "scopes": ["openid", "email", "profile"]
    }
}
