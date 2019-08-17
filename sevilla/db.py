import secrets
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask import current_app

TOKEN_BYTES = 32

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
