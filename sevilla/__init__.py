import os
from datetime import timedelta
from flask import Flask

DEFAULT_CONFIG = {
    "SQLALCHEMY_DATABASE_URI": "sqlite:///../sevilla.db",
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    "SESSION_COOKIE_SECURE": True,
    "SESSION_COOKIE_SAMESITE": "Strict",
    "PERMANENT_SESSION_LIFETIME": timedelta(days=30),
    "MAX_CONTENT_LENGTH": 128 * 1024,
}


def read_env_config(app):
    for key, value in app.config.items():
        if key not in os.environ:
            continue

        env_value = os.environ[key]
        if env_value == "None":
            app.config[key] = None
        elif env_value == "True":
            app.config[key] = True
        elif env_value == "False":
            app.config[key] = False
        else:
            try:
                app.config[key] = int(env_value)
            except ValueError:
                app.config[key] = env_value


def create_app(test_config=None):
    app = Flask(__name__, static_url_path="/", template_folder="static")

    # Apply default config
    app.config.from_mapping(**DEFAULT_CONFIG)

    if not test_config:
        read_env_config(app)
        app.config["SEVILLA_PASSWORD"] = os.environ.get("SEVILLA_PASSWORD")
    else:
        app.config.from_mapping(test_config)

    from sevilla.frontend import frontend
    from sevilla.db import db
    from sevilla.services import AuthService

    app.register_blueprint(frontend)

    db.init_app(app)
    with app.app_context():
        db.create_all()
        AuthService.delete_expired_tokens()

    return app
