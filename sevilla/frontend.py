from functools import wraps
from datetime import datetime, timedelta
from flask import Blueprint, current_app, request, session, redirect, url_for
from flask import abort, render_template
from sevilla.services import AuthService, NotesService
from sevilla.exceptions import (
    PasswordNotSet,
    ModelException,
    NoteNotFound,
    TokenNotFound,
)

frontend = Blueprint("frontend", __name__)


def authenticated(redirect_login=True):
    def wrap(f):
        @wraps(f)
        def wrapped_f(*args, **kwargs):
            if not AuthService.is_valid_token(session.get("id")):
                if redirect_login:
                    return redirect(url_for(".login"))
                else:
                    abort(401)

            return f(*args, **kwargs)

        return wrapped_f

    return wrap


def form_int(key, default=0):
    try:
        return int(request.form.get(key))
    except (ValueError, TypeError):
        return default


def args_int(key, default=0):
    try:
        return int(request.args.get(key))
    except (ValueError, TypeError):
        return default


@frontend.route("/")
@authenticated()
def index():
    return render_template("index.html", note_id=NotesService.generate_note_id())


@frontend.route("/notes")
@authenticated()
def list_notes():
    page = args_int("page", 1)
    pagination = NotesService.paginate_notes(page)

    url_previous = url_for(".list_notes")
    if pagination.prev_num and pagination.prev_num > 1:
        url_previous += "?page={}".format(pagination.prev_num)
    url_next = "{}?page={}".format(url_for(".list_notes"), pagination.next_num)

    return render_template(
        "notes.html",
        pagination=pagination,
        url_previous=url_previous,
        url_next=url_next,
    )


@frontend.route("/notes/<note_id>", methods=["POST"])
@authenticated(redirect_login=False)
def upsert_note(note_id):
    if not NotesService.id_is_valid(note_id):
        abort(400)

    if (request.content_length or 0) > current_app.config["MAX_NOTE_LENGTH"]:
        abort(413)

    timestamp_millis = args_int("timestamp")
    seconds = timestamp_millis // 1000
    millis = timestamp_millis % 1000
    timestamp = datetime.utcfromtimestamp(seconds) + timedelta(milliseconds=millis)
    contents = request.get_data(as_text=True)

    try:
        NotesService.upsert_note(note_id, contents, timestamp)
    except ModelException as e:
        current_app.logger.error(e)
        abort(500)

    current_app.logger.info("Note ID {} created/updated.".format(note_id))

    return {"id": note_id, "timestamp": timestamp_millis}


@frontend.route("/notes/<note_id>")
@authenticated()
def get_note(note_id):
    return render_template("view.html", note=NotesService.get_note(note_id))


@frontend.route("/notes/<note_id>/hide", methods=["POST"])
@authenticated(redirect_login=False)
def hide_note(note_id):
    NotesService.hide_note(note_id)
    page = form_int("page", 1)
    page_size = form_int("pageSize")

    if page_size == 1:
        # We are hiding the last note on the page
        page -= 1

    return redirect(
        url_for(".list_notes") + ("?page={}".format(page) if page > 1 else "")
    )


@frontend.route("/login")
def login_page():
    if AuthService.is_valid_token(session.get("id")):
        return redirect(url_for(".index"))

    return render_template("login.html")


@frontend.route("/login", methods=["POST"])
def login():
    if not AuthService.is_valid_password(request.form.get("password")):
        abort(401)

    session["id"] = AuthService.new_token().id
    session.permanent = True

    current_app.logger.info("New login with ID: {}.".format(session["id"]))
    return redirect(url_for(".index"))


@frontend.route("/logout", methods=["POST"])
@authenticated(redirect_login=False)
def logout():
    AuthService.delete_token(session["id"])
    session.clear()
    return redirect(url_for(".login"))


@frontend.errorhandler(PasswordNotSet)
def handle_password_not_set(_):
    current_app.logger.error("App password ('SEVILLA_PASSWORD') not set.")
    return "Internal server error", 500


@frontend.errorhandler(NoteNotFound)
def handle_note_not_found(_):
    return "Note not found", 404


@frontend.errorhandler(TokenNotFound)
def handle_token_not_found(_):
    return "Token not found", 404
