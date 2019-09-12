from datetime import datetime, timezone
import secrets
from sevilla.db import NOTE_ID_BYTES


def now():
    return datetime.utcnow()


def timestamp_seconds(dt):
    # Ensure the datetime object is aware first
    utc_dt = dt.replace(tzinfo=timezone.utc)
    return int(utc_dt.timestamp())


def generate_note_id():
    return secrets.token_hex(NOTE_ID_BYTES)
