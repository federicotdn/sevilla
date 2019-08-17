from datetime import datetime
from flask import current_app
from sevilla.db import db, Token
from sevilla.exceptions import PasswordNotSet


class AuthService:
    @staticmethod
    def is_valid_password(password):
        app_password = current_app.config.get("SEVILLA_PASSWORD")
        if not app_password:
            raise PasswordNotSet

        return app_password == password

    @staticmethod
    def new_token(expiration=None):
        token = Token(expiration=expiration)
        db.session.add(token)
        db.session.commit()

        return token

    @staticmethod
    def is_valid_token(token_id):
        if not token_id:
            return False

        token = Token.query.get(token_id)
        if not token:
            return False

        if token.expiration < datetime.utcnow():
            return False

        return True
