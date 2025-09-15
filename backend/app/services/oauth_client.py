import httpx
from urllib.parse import urlencode
from typing import Dict, Any, Optional
from fastapi import HTTPException
from app.core.config import OAUTH_PROVIDERS


class OAuthClient: 
    def __init__(self, provider: str):
        if provider not in OAUTH_PROVIDERS:
            raise ValueError(f"Invalid provider: {provider}")
        self.provider = provider
        self.config = OAUTH_PROVIDERS[provider]
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        params = {
            "client_id": self.config["client_id"],
            "redirect_uri": self.config["redirect_uri"],
            "response_type": "code",
            "scope": " ".join(self.config["scopes"]),
        }
        if state:
            params["state"] = state
        return f"{self.config['authorization_url']}?{urlencode(params)}"
    
    async def exchange_code_for_token(self, code: str) -> Optional[Dict[str, Any]]:
        data = {
            "client_id": self.config["client_id"],
            "client_secret": self.config["client_secret"],
            "code": code,
            "redirect_uri": self.config["redirect_uri"],
        }
        
        if self.provider == "google":
            data["grant_type"] = "authorization_code"
            
        headers = {"Accept": "application/json"}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(self.config["token_url"], data=data, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                return None
            
    async def get_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        headers = {"Authorization": f"Bearer {access_token}"}

        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.config["user_info_url"], headers=headers
            )
            
            if response.status_code == 200:
                user_data = response.json()

                if self.provider == "google":
                    return {
                        "id": user_data.get("id"),
                        "email": user_data.get("email"),
                        "name": user_data.get("name"),
                        "first_name": user_data.get("given_name"),
                        "last_name": user_data.get("family_name"),
                        "picture": user_data.get("picture"),
                        "provider": "google"
                    }
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to fetch user info: {response.text}"
                )

            
            
            


        