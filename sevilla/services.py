import secrets
from datetime import datetime
from flask import current_app
from sevilla.db import db, Token, Note
from sevilla.exceptions import PasswordNotSet, NoteNotFound

DEFAULT_MAX_PREVIEW_LENGTH = 20
DEFAULT_PAGE_SIZE = 15


class NotesService:
    @staticmethod
    def id_is_valid(identifier):
        return Note.id_is_valid(identifier)

    @staticmethod
    def upsert_note(note_id, contents, timestamp):
        note = Note.query.get(note_id)
        created = False

        if not note:
            db.session.add(Note(id=note_id, contents=contents, modified=timestamp))
            created = True
        else:
            note.update_contents(contents, timestamp)

        db.session.commit()
        return created

    @staticmethod
    def get_note(note_id):
        if not Note.id_is_valid(note_id):
            raise NoteNotFound

        note = Note.query.get(note_id)
        if not note:
            raise NoteNotFound

        return note

    @staticmethod
    def hide_note(note_id):
        NotesService.get_note(note_id).hidden = True
        db.session.commit()

    @staticmethod
    def _pretty_preview(preview, max_preview_length):
        lines = preview.splitlines()
        first = lines[0]

        if not first.strip():
            return "..."

        if len(first) < max_preview_length and len(lines) == 1:
            return first

        return "{}...".format(first.rstrip())

    @staticmethod
    def note_previews(
        page=1,
        page_size=DEFAULT_PAGE_SIZE,
        max_preview_length=DEFAULT_MAX_PREVIEW_LENGTH,
    ):
        pagination = (
            db.session.query(
                Note.id,
                Note.modified,
                db.func.substr(Note.contents, 1, max_preview_length),
            )
            .filter(Note.hidden == db.false())
            .order_by(Note.modified.desc())
            .paginate(page, per_page=page_size)
        )

        pagination.items = [
            Note.Preview(
                item[0],
                item[1],
                NotesService._pretty_preview(item[2], max_preview_length),
            )
            for item in pagination.items
        ]

        return pagination


class AuthService:
    @staticmethod
    def is_valid_password(password):
        app_password = current_app.config.get("SEVILLA_PASSWORD")
        if not app_password:
            raise PasswordNotSet

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
    def delete_expired_tokens():
        Token.query.filter(Token.expiration < datetime.utcnow()).delete()
        db.session.commit()
