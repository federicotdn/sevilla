from sevilla.frontend import is_note_link
from sevilla.services import NotesService
from tests import BaseTest, utils
from tests.test_notes_service import VALID_ID


class TestFrontend(BaseTest):
    def setUp(self):
        super().setUp()
        self.client.post(
            "/login", data={"password": self.app.config["SEVILLA_PASSWORD"]}
        )

    def test_logout(self):
        rv = self.client.get("/")
        self.assertEqual(rv.status_code, 200)

        rv = self.client.post("/logout")
        self.assertEqual(rv.status_code, 302)

        rv = self.client.post("/notes/" + VALID_ID)
        self.assertEqual(rv.status_code, 401)

    def test_create_note(self):
        rv = self.client.post(
            "/notes/" + VALID_ID + "?timestamp=1",
            data="Hello, world!",
            headers={"Content-type": "text/plain"},
        )
        self.assertEqual(rv.status_code, 200)

        note = NotesService.get_note(VALID_ID)
        self.assertEqual(note.contents, "Hello, world!")

    def test_create_empty_note(self):
        rv = self.client.post(
            "/notes/" + VALID_ID + "?timestamp=1",
            data="",
            headers={"Content-type": "text/plain"},
        )
        self.assertEqual(rv.status_code, 200)

        note = NotesService.get_note(VALID_ID)
        self.assertEqual(note.contents, "")

    def test_update_note(self):
        rv = self.client.post(
            "/notes/" + VALID_ID + "?timestamp=1000",
            data="foo",
            headers={"Content-type": "text/plain"},
        )
        self.assertEqual(rv.status_code, 200)

        rv = self.client.post(
            "/notes/" + VALID_ID + "?timestamp=2000",
            data="bar",
            headers={"Content-type": "text/plain"},
        )
        self.assertEqual(rv.status_code, 200)

        note = NotesService.get_note(VALID_ID)
        self.assertEqual(note.contents, "bar")
        self.assertEqual(utils.timestamp_seconds(note.modified), 2)

    def test_try_update_note(self):
        rv = self.client.post(
            "/notes/" + VALID_ID + "?timestamp=2000",
            data="foo",
            headers={"Content-type": "text/plain"},
        )
        self.assertEqual(rv.status_code, 200)

        # Try sending again with older timestamp
        rv = self.client.post(
            "/notes/" + VALID_ID + "?timestamp=1000",
            data="bar",
            headers={"Content-type": "text/plain"},
        )
        self.assertEqual(rv.status_code, 200)

        note = NotesService.get_note(VALID_ID)
        self.assertEqual(note.contents, "foo")
        self.assertEqual(utils.timestamp_seconds(note.modified), 2)

    def test_try_update_note_invalid_timestamp(self):
        rv = self.client.post(
            "/notes/" + VALID_ID + "?timestamp=2000",
            data="foo",
            headers={"Content-type": "text/plain"},
        )
        self.assertEqual(rv.status_code, 200)

        # Try sending again with invalid timestamp
        rv = self.client.post(
            "/notes/" + VALID_ID + "?timestamp=foobar",
            data="bar",
            headers={"Content-type": "text/plain"},
        )
        self.assertEqual(rv.status_code, 200)

        note = NotesService.get_note(VALID_ID)
        self.assertEqual(note.contents, "foo")
        self.assertEqual(utils.timestamp_seconds(note.modified), 2)

    def test_try_large_upload(self):
        self.app.config["MAX_NOTE_LENGTH"] = 5

        rv = self.client.post(
            "/notes/" + VALID_ID + "?timestamp=1",
            data="abcd",
            headers={"Content-type": "text/plain"},
        )
        self.assertEqual(rv.status_code, 200)

        rv = self.client.post(
            "/notes/" + VALID_ID + "?timestamp=2",
            data="abcdefgh",
            headers={"Content-type": "text/plain"},
        )
        self.assertEqual(rv.status_code, 413)

    def test_hide_note(self):
        params_list = [
            {"page": 1, "pageSize": 10},
            {"page": 1},
            {"page": "foobar"},
            {"page": "foobar", "pageSize": "foo"},
        ]
        NotesService.upsert_note(VALID_ID, "hello", utils.now())

        for params in params_list:
            with self.subTest(**params):
                rv = self.client.post("/notes/" + VALID_ID + "/hide", data=params)

                self.assertEqual(rv.status_code, 302)
                self.assertTrue(NotesService.get_note(VALID_ID).hidden)

    def test_hide_invalid(self):
        note_ids = [VALID_ID, "foobar"]

        for note_id in note_ids:
            with self.subTest(note_id=note_id):
                rv = self.client.post("/notes/" + note_id + "/hide")
                self.assertEqual(rv.status_code, 404)

    def test_view_index(self):
        with self.client.get("/") as rv:
            self.assertEqual(rv.status_code, 200)

    def test_view_notes_empty(self):
        with self.client.get("/notes") as rv:
            self.assertEqual(rv.status_code, 200)

    def test_view_notes(self):
        for _ in range(50):
            NotesService.upsert_note(
                NotesService.generate_note_id(), "hello", utils.now()
            )

        urls = ["/notes", "/notes?page=1", "/notes?page=foobar"]

        for url in urls:
            with self.subTest(url=url):
                with self.client.get(url) as rv:
                    self.assertEqual(rv.status_code, 200)

    def test_view_notes_range(self):
        with self.client.get("/notes?page=1000") as rv:
            self.assertEqual(rv.status_code, 404)

    def test_view_note(self):
        NotesService.upsert_note(VALID_ID, "hello", utils.now())
        with self.client.get("/notes/" + VALID_ID) as rv:
            self.assertEqual(rv.status_code, 200)

    def test_view_note_invalid(self):
        with self.client.get("/notes/" + VALID_ID) as rv:
            self.assertEqual(rv.status_code, 404)

        with self.client.get("/notes/abc") as rv:
            self.assertEqual(rv.status_code, 404)

    def test_note_is_link(self):
        notes = [
            ("http://example.com", True),
            ("https://place.com", True),
            ("https://place.com/foobar", True),
            ("https://place.com/foobar#foo", True),
            ("https://place.com/foobar?q=hello", True),
            ("hello there", False),
            ("something\nsomething", False),
            ("http://hello.com\nmore stuff", False),
            ("", False),
        ]

        for note, is_link in notes:
            with self.subTest(note=note):
                note = NotesService.upsert_note(VALID_ID, note, utils.now())
                self.assertEqual(is_note_link(note), is_link)


class TestFrontendNoLogin(BaseTest):
    def test_view_login(self):
        with self.client.get("/login") as rv:
            self.assertEqual(rv.status_code, 200)

    def test_login_fail(self):
        rv = self.client.post("/login")
        self.assertEqual(rv.status_code, 401)

        rv = self.client.post("/login", data={"password": "foobar"})
        self.assertEqual(rv.status_code, 401)

    def test_upsert_note_unauthorized(self):
        rv = self.client.post("/notes/" + VALID_ID)
        self.assertEqual(rv.status_code, 401)

    def test_hide_note_unauthorized(self):
        rv = self.client.post("/notes/" + VALID_ID + "/hide")
        self.assertEqual(rv.status_code, 401)

    def test_view_index_redirect(self):
        rv = self.client.get("/")
        self.assertEqual(rv.status_code, 302)

    def test_view_notes_redirect(self):
        rv = self.client.get("/notes")
        self.assertEqual(rv.status_code, 302)

    def test_view_note_redirect(self):
        rv = self.client.get("/notes/" + VALID_ID)
        self.assertEqual(rv.status_code, 302)
