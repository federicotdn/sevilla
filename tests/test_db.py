from sevilla.db import Token, Note
from sevilla.exceptions import ModelException
from tests.test_notes_service import VALID_ID
from tests import BaseTest, utils


class TestDB(BaseTest):
    def test_try_create_token_with_id(self):
        with self.assertRaises(ValueError):
            Token(id="hello")

    def test_try_create_note_with_invalid_id(self):
        with self.assertRaises(ModelException):
            Note(id="hello", contents="", modified=utils.now())

    def test_try_create_note_with_large_contents(self):
        self.app.config["MAX_NOTE_LENGTH"] = 2

        with self.assertRaises(ModelException):
            Note(id=VALID_ID, contents="foobar", modified=utils.now())
