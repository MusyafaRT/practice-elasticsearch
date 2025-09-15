from app.db.mongodb import get_activity_collection
from app.models.activity_log import ActivityLog, ActionEnum
from typing import Optional
from pydantic import UUID4

def log_activity(action: ActionEnum, user_id: Optional[UUID4] = None, last_name: Optional[str] = None, details: Optional[dict] = None):
    collection = get_activity_collection()
    log = ActivityLog(user_id=user_id, last_name=last_name, action=action, details=details)
    
    log_dict = log.dict()
    if log_dict["user_id"] is not None:
        log_dict["user_id"] = str(log_dict["user_id"]) 
        
    collection.insert_one(log_dict)
    return {"status": "logged", "data": log.dict()}

def get_logs(limit: int = 10):
    collection = get_activity_collection()
    logs = list(collection.find().sort("timestamp", -1).limit(limit))
    for log in logs:
        log["_id"] = str(log["_id"])
    return logs
