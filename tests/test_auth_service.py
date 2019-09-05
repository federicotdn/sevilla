from tests import BaseTest, utils
from datetime import datetime, timedelta
from sevilla.services import AuthService
from sevilla.exceptions import PasswordNotSet
from sevilla.db import Token, TOKEN_BYTES

EXAMPLE_TOKEN = "6eea0242e12afb9fc604b15ac98c2c5f71c46f453c84db9995ebdb3c14523bb4"


class TestAuthService(BaseTest):
    def test_no_password_set(self):
        self.app.config["SEVILLA_PASSWORD"] = None
        with self.assertRaises(PasswordNotSet):
            AuthService.is_valid_password("")

    def test_password_correct(self):
        self.assertTrue(AuthService.is_valid_password("sevilla"))

    def test_password_incorrect(self):
        self.assertFalse(AuthService.is_valid_password("foobar"))

    def test_new_token(self):
        token = AuthService.new_token()
        self.assertEqual(len(token.id), TOKEN_BYTES * 2)
        diff = (
            datetime.utcnow()
            + timedelta(seconds=self.app.config["PERMANENT_SESSION_LIFETIME"])
        ) - token.expiration

        self.assertLess(diff.total_seconds(), 5)

    def test_invalid_token(self):
        expired_token = AuthService.new_token(
            expiration=utils.now() - timedelta(days=10)
        )

        tokens = ["", "hello", EXAMPLE_TOKEN, expired_token.id]
        for token in tokens:
            with self.subTest(token=token):
                self.assertFalse(AuthService.is_valid_token(token))

    def test_valid_token(self):
        token = AuthService.new_token()
        self.assertTrue(AuthService.is_valid_token(token.id))

    def test_delete_expired_tokens(self):
        AuthService.new_token(expiration=utils.now() - timedelta(days=10))
        self.assertEqual(Token.query.count(), 1)
        AuthService.delete_expired_tokens()
        self.assertEqual(Token.query.count(), 0)
