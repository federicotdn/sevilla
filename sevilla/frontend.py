from flask import Blueprint, current_app

frontend = Blueprint("frontend", __name__)


@frontend.route("/")
def index():
    return current_app.send_static_file("index.html")


@frontend.route("/notes")
def notes():
    return current_app.send_static_file("notes.html")
