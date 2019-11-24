from flask import current_app

I18N = {
    "en": {
        "login": "Login",
        "password": "Password",
        "note_placeholder": "Write or paste here",
        "write": "Write",
        "logout": "Log out",
        "note": "Note",
        "created": "Created",
        "hide": "Hide",
        "first": "Page 1",
        "no_notes": "No notes to show.",
        "empty": "empty",
        "invalid_password": "Invalid password.",
        "internal_server_error": "Internal server error",
        "note_not_found": "Note not found",
        "token_not_found": "Token not found",
    },
    "es": {
        "login": "Iniciar",
        "password": "Contraseña",
        "note_placeholder": "Escribir o pegar aquí",
        "write": "Escribir",
        "logout": "Cerrar Sesión",
        "note": "Nota",
        "created": "Creación",
        "hide": "Esc.",
        "first": "Pág. 1",
        "no_notes": "No hay notas para mostrar.",
        "empty": "vacía",
        "invalid_password": "Contraseña inválida.",
        "internal_server_error": "Error interno del servidor",
        "note_not_found": "Nota no encontrada",
        "token_not_found": "Token no encontrado",
    },
}


class Translator:
    def __init__(self, app=None):
        self._locale = None
        self._dict = {}
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self._locale = app.config["SEVILLA_LOCALE"]
        self._dict = I18N.get(self._locale, {})

    def __getattr__(self, name):
        val = self._dict.get(name)
        if val is None:
            current_app.logger.warning(
                "Untranslated message: '{}' (locale: '{}').".format(name, self._locale)
            )

            val = I18N["en"].get(name)
            if val is None:
                raise AttributeError

        return val


t = Translator()
