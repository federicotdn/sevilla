import unittest
from sevilla import create_app


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app(
            {
                "SQLALCHEMY_DATABASE_URI": "sqlite://",
                "SECRET_KEY": "testing-key",
                "SEVILLA_PASSWORD": "sevilla",
            }
        )

        self.ctx = self.app.app_context()
        self.ctx.push()
        self.client = self.app.test_client()

    def tearDown(self):
        self.client = None
        self.ctx.pop()
        self.ctx = None
        self.app = None
