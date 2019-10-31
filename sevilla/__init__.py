import os
import logging
from flask import Flask

DEFAULT_CONFIG = {
    "SQLALCHEMY_DATABASE_URI": None,
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    "SESSION_COOKIE_SECURE": True,
    "SESSION_COOKIE_SAMESITE": "Lax",
    "PERMANENT_SESSION_LIFETIME": 2678400,  # 31 days in seconds
    "MAX_NOTE_LENGTH": 128 * 1024,
    "SEVILLA_PASSWORD": None,
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
    else:
        app.config.from_mapping(test_config)

    from sevilla.frontend import frontend
    from sevilla.db import db, migrate, upgrade_db
    from sevilla.services import AuthService

    app.register_blueprint(frontend)

    db.init_app(app)
    migrate.init_app(app)

    with app.app_context():
        if test_config:
            db.create_all()
        else:
            upgrade_db()

        deleted = AuthService.delete_expired_tokens()

    if os.environ.get("SERVER_SOFTWARE", "").startswith("gunicorn"):
        gunicorn_logger = logging.getLogger("gunicorn.error")
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)

    if deleted:
        app.logger.info("Deleted {} expired user token(s).".format(deleted))

    return app
