from pydantic import BaseModel, UUID4
from typing import Optional
from enum import Enum
from datetime import datetime

class ActionEnum(str, Enum):
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"

class ActivityLog(BaseModel):
    user_id: Optional[UUID4] = None
    last_name: Optional[str] = None
    action: ActionEnum
    details: Optional[dict] = None
    timestamp: datetime = datetime.utcnow()
