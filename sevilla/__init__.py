import os

from flask import Flask


def create_app(test_config=None):
    app = Flask(
        __name__,
        instance_relative_config=True,
        static_folder="static",
        static_url_path="/",
    )

    if not test_config:
        app.config.from_pyfile("sevilla.cfg", silent=True)
    else:
        app.config.from_mapping(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

    from sevilla.frontend import frontend

    app.register_blueprint(frontend)

    return app
