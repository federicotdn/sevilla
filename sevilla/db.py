import secrets
import string
from datetime import datetime, timedelta, timezone
from flask_sqlalchemy import SQLAlchemy
from flask import current_app
from sevilla.exceptions import ModelException

TOKEN_BYTES = 32
NOTE_ID_BYTES = 16
DEFAULT_MAX_PREVIEW_LENGTH = 20

db = SQLAlchemy()


class Token(db.Model):
    id = db.Column(db.String(TOKEN_BYTES * 2), primary_key=True)
    expiration = db.Column(db.DateTime, nullable=False)

    def __init__(self, **kwargs):
        if "id" in kwargs:
            raise ValueError("ID must not be specified for new tokens.")

        kwargs["id"] = secrets.token_hex(TOKEN_BYTES)

        if not kwargs.get("expiration"):
            kwargs["expiration"] = datetime.utcnow() + timedelta(
                seconds=current_app.config["PERMANENT_SESSION_LIFETIME"]
            )

        super().__init__(**kwargs)


class Note(db.Model):
    id = db.Column(db.String(NOTE_ID_BYTES * 2), primary_key=True)
    contents = db.Column(db.Text, nullable=False)
    modified = db.Column(db.DateTime, nullable=False)
    hidden = db.Column(db.Boolean, nullable=False, default=False)

    def update_contents(self, contents, timestamp):
        if self.modified < timestamp:
            self.contents = contents
            self.modified = timestamp

    def hide(self):
        self.hidden = True

    def preview(self, preview_length=DEFAULT_MAX_PREVIEW_LENGTH):
        lines = self.contents.splitlines()
        first = lines[0].strip() if lines else ""

        if not first:
            return "..."

        if len(first) <= preview_length and len(lines) == 1:
            return first

        return "{}...".format(first[:preview_length])

    def modified_millis(self):
        # Ensure the datetime object is aware first
        utc_dt = self.modified.replace(tzinfo=timezone.utc)
        return int(utc_dt.timestamp() * 1000)

    @classmethod
    def id_is_valid(cls, identifier):
        return (
            identifier
            and all(c in string.hexdigits for c in identifier)
            and len(identifier) == NOTE_ID_BYTES * 2
        )

    @db.validates("contents")
    def validate_contents(self, _key, contents):
        max_len = current_app.config["MAX_NOTE_LENGTH"]
        if len(contents) > max_len:
            raise ModelException(
                "Max note length is {}. Got: {}.".format(max_len, len(contents))
            )

        return contents

    @db.validates("id")
    def validate_id(self, _key, identifier):
        if not self.id_is_valid(identifier):
            raise ModelException(
                "Note ID must be a hexadecimal string of length {}. Got: '{}'.".format(
                    NOTE_ID_BYTES * 2, identifier
                )
            )

        return identifier
