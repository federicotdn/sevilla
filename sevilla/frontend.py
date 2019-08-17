from functools import wraps
from flask import Blueprint, current_app, request, session, redirect, url_for
from flask import abort

frontend = Blueprint("frontend", __name__)


def redirect_login(f):
    @wraps(f)
    def fn(*args, **kwargs):
        if "authenticated" not in session:
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


@frontend.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("password") == "sevilla":
            session["authenticated"] = True
            session.permanent = True
            return redirect(url_for(".notes"))
        else:
            abort(401)

    # GET
    if "authenticated" in session:
        return redirect(url_for(".notes"))

    return current_app.send_static_file("login.html")
