import json
from flask import current_app

STRINGS_DATA_PATH = "sevilla/strings.json"


class Translator:
    def __init__(self, app=None, data=None):
        if data:
            self._data = data
        else:
            with open(STRINGS_DATA_PATH) as f:
                self._data = json.load(f)

        self._locale = None
        self._dict = {}
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self._locale = app.config["SEVILLA_LOCALE"]
        self._dict = self._data.get(self._locale, {})

    def __getattr__(self, name):
        val = self._dict.get(name)
        if val is None:
            current_app.logger.warning(
                "Untranslated message: '{}' (locale: '{}').".format(name, self._locale)
            )

            val = self._data.get("en", {}).get(name)
            if val is None:
                raise AttributeError

        return val


t = Translator()
