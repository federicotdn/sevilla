from functools import wraps
from datetime import datetime, timedelta
from flask import Blueprint, current_app, request, session, redirect, url_for
from flask import abort, render_template
from sevilla.services import AuthService, NotesService
from sevilla.exceptions import PasswordNotSet, ModelException

frontend = Blueprint("frontend", __name__)


def redirect_login(f):
    @wraps(f)
    def fn(*args, **kwargs):
        if not AuthService.is_valid_token(session.get("id")):
            return redirect(url_for(".login"))

        return f(*args, **kwargs)

    return fn


@frontend.route("/")
@redirect_login
def index():
    return current_app.send_static_file("index.html")


@frontend.context_processor
def natural_datetime():
    def fn(dt):
        return "Date: {}".format(dt)

    return {"natural_datetime": fn}


@frontend.route("/notes")
@redirect_login
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


@frontend.route("/notes", methods=["POST"])
def upsert_note():
    if not AuthService.is_valid_token(session.get("id")):
        abort(401)

    note_id = request.args.get("id")
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
@redirect_login
def get_note(note_id):
    if not NotesService.id_is_valid(note_id):
        abort(400)

    note = NotesService.get_note(note_id)
    if not note:
        abort(404)

    return note.contents


@frontend.route("/login")
def login_page():
    if AuthService.is_valid_token(session.get("id")):
        return redirect(url_for(".index"))

    return current_app.send_static_file("login.html")


@frontend.route("/login", methods=["POST"])
def login():
    if AuthService.is_valid_password(request.form.get("password")):
        token = AuthService.new_token()
        session["id"] = token.id
        session.permanent = True

        current_app.logger.info("New login with ID: {}.".format(session["id"]))
        return redirect(url_for(".index"))
    else:
        abort(401)


@frontend.errorhandler(PasswordNotSet)
def handle_password_not_set(_):
    current_app.logger.error("App password ('SEVILLA_PASSWORD') not set.")
    return "Internal server error", 500
