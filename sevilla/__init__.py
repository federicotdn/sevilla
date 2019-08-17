import os
from datetime import timedelta
from flask import Flask

DEFAULT_CONFIG = {
    "SQLALCHEMY_DATABASE_URI": "sqlite:///../sevilla.db",
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    "SESSION_COOKIE_SECURE": True,
    "SESSION_COOKIE_SAMESITE": "Strict",
    "PERMANENT_SESSION_LIFETIME": timedelta(days=30),
}


def create_app(test_config=None):
    app = Flask(
        __name__,
        instance_relative_config=True,
        static_folder="static",
        static_url_path="/",
    )

    if not test_config:
        # Apply default config
        app.config.from_mapping(**DEFAULT_CONFIG)

        # Apply user config
        app.config.from_pyfile("sevilla.cfg")

        # Overwrite with env config (useful for development)
        if os.environ.get("SESSION_COOKIE_SECURE") == "False":
            app.config["SESSION_COOKIE_SECURE"] = False

        if "SECRET_KEY" in os.environ:
            app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]

        if "SEVILLA_PASSWORD" in os.environ:
            app.config["SEVILLA_PASSWORD"] = os.environ["SEVILLA_PASSWORD"]
    else:
        app.config.from_mapping(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

    from sevilla.frontend import frontend
    from sevilla.db import db

    app.register_blueprint(frontend)
    db.init_app(app)
    with app.app_context():
        db.create_all()

    return app
