from datetime import datetime, timezone, timedelta


def now(offset_seconds=0):
    return datetime.utcnow() + timedelta(seconds=offset_seconds)


def timestamp_seconds(dt):
    # Ensure the datetime object is aware first
    utc_dt = dt.replace(tzinfo=timezone.utc)
    return int(utc_dt.timestamp())
