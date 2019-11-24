import logging
from tests import BaseTest
from sevilla.strings import t, Translator


class TestTranslator(BaseTest):
    def test_translate(self):
        self.assertEqual(t.note, "Note")

    def test_no_attribute(self):
        self.app.logger.setLevel(logging.ERROR)
        with self.assertRaises(AttributeError):
            t.foobar

    def test_default(self):
        self.app.logger.setLevel(logging.ERROR)
        self.app.config["SEVILLA_LOCALE"] = "foo"

        t_aux = Translator(self.app, {"foo": {}, "en": {"bar": "baz"}})

        self.assertEqual(t_aux.bar, "baz")
