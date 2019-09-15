from datetime import datetime, timezone


def now():
    return datetime.utcnow()


def timestamp_seconds(dt):
    # Ensure the datetime object is aware first
    utc_dt = dt.replace(tzinfo=timezone.utc)
    return int(utc_dt.timestamp())
