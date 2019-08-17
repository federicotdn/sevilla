from functools import wraps
from flask import Blueprint, current_app, request, session, redirect, url_for
from flask import abort
from sevilla.services import AuthService
from sevilla.exceptions import PasswordNotSet

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


@frontend.route("/notes")
@redirect_login
def notes():
    return current_app.send_static_file("notes.html")


@frontend.route("/login")
def login_page():
    if AuthService.is_valid_token(session.get("id")):
        return redirect(url_for(".notes"))

    return current_app.send_static_file("login.html")


@frontend.route("/login", methods=["POST"])
def login():
    if AuthService.is_valid_password(request.form.get("password")):
        token = AuthService.new_token()
        session["id"] = token.id
        session.permanent = True
        return redirect(url_for(".notes"))
    else:
        abort(401)


@frontend.errorhandler(PasswordNotSet)
def handle_password_not_set(_):
    current_app.logger.error("App password ('SEVILLA_PASSWORD') not set.")
    return "Internal server error", 500
