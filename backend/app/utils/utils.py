from datetime import datetime, timezone

def format_datetime_for_es(dt: datetime | None) -> str:
    if not dt:
        return ""
    # convert ke UTC dan kirim tanpa offset
    return dt.astimezone(timezone.utc).replace(tzinfo=None).isoformat()