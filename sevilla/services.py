import secrets
from datetime import datetime
from flask import current_app
from sevilla.db import db, Token, Note
from sevilla.exceptions import PasswordNotSet, NoteNotFound, TokenNotFound

DEFAULT_PAGE_SIZE = 15


class NotesService:
    @staticmethod
    def id_is_valid(identifier):
        return Note.id_is_valid(identifier)

    @staticmethod
    def upsert_note(note_id, contents, timestamp):
        note = Note.query.get(note_id)

        if not note:
            note = Note(id=note_id, contents=contents, modified=timestamp)
            db.session.add(note)
        else:
            note.update_contents(contents, timestamp)

        db.session.commit()
        return note

    @staticmethod
    def get_note(note_id):
        if not Note.id_is_valid(note_id):
            raise NoteNotFound

        note = Note.query.get(note_id)
        if not note:
            raise NoteNotFound

        return note

    @staticmethod
    def mark_as_read(note):
        note.mark_as_read()
        db.session.commit()

    @staticmethod
    def generate_note_id():
        return Note.generate_id()

    @staticmethod
    def hide_note(note_id):
        NotesService.get_note(note_id).hidden = True
        db.session.commit()

    @staticmethod
    def notes(yield_per=100):
        return (
            Note.query.filter(Note.hidden == db.false())
            .order_by(Note.modified.desc())
            .yield_per(yield_per)
        )

    @staticmethod
    def paginate_notes(page, page_size=DEFAULT_PAGE_SIZE):
        return (
            Note.query.filter(Note.hidden == db.false())
            .order_by(Note.modified.desc())
            .paginate(page, per_page=page_size)
        )


class AuthService:
    @staticmethod
    def is_valid_password(password):
        app_password = current_app.config.get("SEVILLA_PASSWORD")
        if not app_password:
            raise PasswordNotSet

        if not password:
            return False

        return secrets.compare_digest(app_password, password)

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

        return token.expiration > datetime.utcnow()

    @staticmethod
    def delete_token(token_id):
        token = Token.query.get(token_id)
        if not token:
            raise TokenNotFound

        db.session.delete(token)
        db.session.commit()

    @staticmethod
    def delete_expired_tokens():
        deleted = Token.query.filter(Token.expiration < datetime.utcnow()).delete()
        db.session.commit()
        return deleted
