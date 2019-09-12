from sevilla.db import Token, Note
from sevilla.exceptions import ModelException
from tests import BaseTest, utils


class TestDB(BaseTest):
    def test_try_create_token_with_id(self):
        with self.assertRaises(ValueError):
            Token(id="hello")

    def test_try_create_note_with_invalid_id(self):
        with self.assertRaises(ModelException):
            Note(id="hello", contents="", modified=utils.now())
