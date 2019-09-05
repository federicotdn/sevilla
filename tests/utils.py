from datetime import datetime
import secrets
from sevilla.db import NOTE_ID_BYTES


def now():
    return datetime.utcnow()


def generate_note_id():
    return secrets.token_hex(NOTE_ID_BYTES)
