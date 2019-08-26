from functools import wraps
from datetime import datetime, timedelta, timezone
from flask import Blueprint, current_app, request, session, redirect, url_for
from flask import abort, render_template
from sevilla.services import AuthService, NotesService
from sevilla.exceptions import PasswordNotSet, ModelException, NoteNotFound

frontend = Blueprint("frontend", __name__)


def authenticated(redirect=True):
    def wrap(f):
        @wraps(f)
        def wrapped_f(*args, **kwargs):
            if not AuthService.is_valid_token(session.get("id")):
                if redirect:
                    return redirect(url_for(".login"))
                else:
                    abort(401)

            return f(*args, **kwargs)

        return wrapped_f

    return wrap


@frontend.context_processor
def timestamp_millis():
    def fn(dt):
        # Ensure the datetime object is aware first
        utc_dt = dt.replace(tzinfo=timezone.utc)
        return int(utc_dt.timestamp() * 1000)

    return {"timestamp_millis": fn}


@frontend.route("/")
@authenticated()
def index():
    return current_app.send_static_file("index.html")


@frontend.route("/notes")
@authenticated()
def list_notes():
    try:
        page = int(request.args.get("page") or 1)
    except ValueError:
        abort(400)

    pagination = NotesService.note_previews(page)

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
@authenticated(redirect=False)
def upsert_note(note_id):
    if not NotesService.id_is_valid(note_id):
        abort(400)

    try:
        timestamp_millis = int(request.args.get("timestamp"))
    except (ValueError, TypeError):
        abort(400)

    seconds = timestamp_millis // 1000
    millis = timestamp_millis % 1000
    timestamp = datetime.utcfromtimestamp(seconds) + timedelta(milliseconds=millis)
    contents = request.get_data(as_text=True)

    try:
        created = NotesService.upsert_note(note_id, contents, timestamp)
    except ModelException as e:
        current_app.logger.error(e)
        abort(500)

    if created:
        current_app.logger.info("New note created with ID: {}.".format(note_id))
    else:
        current_app.logger.info("Updated note with ID: {}.".format(note_id))

    return {"id": note_id, "timestamp": timestamp_millis}


@frontend.route("/notes/<note_id>")
@authenticated()
def get_note(note_id):
    if not NotesService.id_is_valid(note_id):
        abort(400)

    return render_template("view.html", note=NotesService.get_note(note_id))


@frontend.route("/notes/<note_id>/hide", methods=["POST"])
@authenticated()
def hide_note(note_id):
    NotesService.hide_note(note_id)
    page = int(request.form.get("page"))
    page_size = int(request.form.get("pageSize"))

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

    return current_app.send_static_file("login.html")


@frontend.route("/login", methods=["POST"])
def login():
    if AuthService.is_valid_password(request.form.get("password")):
        session["id"] = AuthService.new_token().id
        session.permanent = True

        current_app.logger.info("New login with ID: {}.".format(session["id"]))
        return redirect(url_for(".index"))
    else:
        abort(401)


@frontend.errorhandler(PasswordNotSet)
def handle_password_not_set(_):
    current_app.logger.error("App password ('SEVILLA_PASSWORD') not set.")
    return "Internal server error", 500


@frontend.errorhandler(NoteNotFound)
def handle_note_not_found(_):
    return "Note not found", 404
