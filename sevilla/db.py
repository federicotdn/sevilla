import secrets
import string
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask import current_app
from sevilla.exceptions import ModelException

TOKEN_BYTES = 32
NOTE_ID_BYTES = 16

db = SQLAlchemy()


class Token(db.Model):
    id = db.Column(db.String(TOKEN_BYTES * 2), primary_key=True)
    expiration = db.Column(db.DateTime, nullable=False)

    def __init__(self, **kwargs):
        if "id" in kwargs:
            raise ValueError("ID must not be specified for new tokens.")

        kwargs["id"] = secrets.token_hex(TOKEN_BYTES)

        if not kwargs.get("expiration"):
            kwargs["expiration"] = (
                datetime.utcnow() + current_app.config["PERMANENT_SESSION_LIFETIME"]
            )

        super().__init__(**kwargs)


class Note(db.Model):
    id = db.Column(db.String(NOTE_ID_BYTES * 2), primary_key=True)
    contents = db.Column(db.Text, nullable=False)
    modified = db.Column(db.DateTime, nullable=False)
    hidden = db.Column(db.Boolean, nullable=False, default=False)
    preview = None

    def update_contents(self, contents, timestamp):
        if self.modified < timestamp:
            self.contents = contents
            self.modified = timestamp

    def hide(self):
        self.hidden = True

    @classmethod
    def id_is_valid(cls, identifier):
        return (
            identifier
            and all(c in string.hexdigits for c in identifier)
            and len(identifier) == NOTE_ID_BYTES * 2
        )

    @db.validates("id")
    def validate_id(self, _key, identifier):
        if not self.id_is_valid(identifier):
            raise ModelException(
                "Note ID must be a hexadecimal string of length {}. Got: '{}'.".format(
                    NOTE_ID_BYTES * 2, identifier
                )
            )

        return identifier
