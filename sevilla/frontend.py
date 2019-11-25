import urllib.parse
import io
import zipfile
from functools import wraps
from datetime import datetime, timedelta
from flask import Blueprint, current_app, request, session, redirect, url_for, flash
from flask import abort, render_template, send_file
from sevilla.services import AuthService, NotesService
from sevilla.strings import t
from sevilla.exceptions import (
    PasswordNotSet,
    ModelException,
    NoteNotFound,
    TokenNotFound,
)

frontend = Blueprint("frontend", __name__)


def authenticated(show_login=True):
    def wrap(f):
        @wraps(f)
        def wrapped_f(*args, **kwargs):
            current_app.logger.info("Session ID: {}.".format(session.get("id")))

            if not AuthService.is_valid_token(session.get("id")):
                current_app.logger.info("Session not valid.")

                if show_login:
                    return render_template("login.html", next=request.path, t=t)
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


def args_bool(key):
    return key in request.args


def is_note_link(note):
    lines = note.contents.splitlines()
    if len(lines) != 1:
        return False

    parts = lines[0].split()
    if len(parts) != 1:
        return False

    scheme = urllib.parse.urlparse(parts[0]).scheme
    return scheme in ["https", "http"]


@frontend.route("/")
@authenticated()
def index():
    return render_template("index.html", note_id=NotesService.generate_note_id(), t=t)


def dump():
    f = io.BytesIO()
    with zipfile.ZipFile(f, "w") as zf:
        for note in NotesService.notes():
            data = zipfile.ZipInfo("{}.txt".format(note.id), note.modified.timetuple())
            zf.writestr(data, note.contents)

    f.seek(0)
    return send_file(f, attachment_filename="notes.zip", as_attachment=True)


@frontend.route("/notes")
@authenticated()
def get_notes():
    if args_bool("dump"):
        return dump()

    page = args_int("page", 1)
    pagination = NotesService.paginate_notes(page)

    url_previous = url_for(".get_notes")
    if pagination.prev_num and pagination.prev_num > 1:
        url_previous += "?page={}".format(pagination.prev_num)
    url_next = "{}?page={}".format(url_for(".get_notes"), pagination.next_num)

    return render_template(
        "notes.html",
        pagination=pagination,
        url_previous=url_previous,
        url_next=url_next,
        t=t,
    )


@frontend.route("/notes/<note_id>", methods=["PUT"])
@authenticated(show_login=False)
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
    except ModelException:
        current_app.logger.exception("Error storing note:")
        abort(500)

    current_app.logger.info("Note ID {} created/updated.".format(note_id))

    return {"id": note_id, "timestamp": timestamp_millis}


@frontend.route("/notes/<note_id>")
@authenticated()
def get_note(note_id):
    note = NotesService.get_note(note_id)
    NotesService.mark_as_read(note)

    is_link = is_note_link(note)
    template = "view-link.html" if is_link else "view.html"

    return render_template(template, contents=note.contents)


@frontend.route("/notes/<note_id>/hide", methods=["POST"])
@authenticated(show_login=False)
def hide_note(note_id):
    NotesService.hide_note(note_id)
    page = form_int("page", 1)
    page_size = form_int("pageSize")

    if page_size == 1:
        # We are hiding the last note on the page
        page -= 1

    return redirect(
        url_for(".get_notes") + ("?page={}".format(page) if page > 1 else "")
    )


@frontend.route("/session/login", methods=["POST"])
def login():
    if not AuthService.is_valid_password(request.form.get("password")):
        flash(t.invalid_password, "error")
        return redirect(url_for(".index"))

    session["id"] = AuthService.new_token().id
    session.permanent = True

    current_app.logger.info("New login with ID: {}.".format(session["id"]))
    return redirect(request.form.get("next", url_for(".index")))


@frontend.route("/session/logout", methods=["POST"])
@authenticated(show_login=False)
def logout():
    AuthService.delete_token(session["id"])
    session.clear()
    return redirect(url_for(".index"))


@frontend.errorhandler(PasswordNotSet)
def handle_password_not_set(_):
    current_app.logger.error("App password ('SEVILLA_PASSWORD') not set.")
    return t.internal_server_error, 500


@frontend.errorhandler(NoteNotFound)
def handle_note_not_found(_):
    return t.note_not_found, 404


@frontend.errorhandler(TokenNotFound)
def handle_token_not_found(_):
    return t.token_not_found, 404
