import unittest
from requests import Session
from sevilla.db import Note

BASE_URL = "http://localhost:8080"


class TestDockerService(unittest.TestCase):
    def test_docker_service(self):
        s = Session()
        note_id = Note.generate_id()
        note_text = "Hello, World!"

        # Try creating a note before logging in
        resp = s.put(
            BASE_URL + "/notes/" + note_id, params={"timestamp": 2}, data=note_text
        )
        self.assertEqual(resp.status_code, 401)

        # Log in
        resp = s.post(BASE_URL + "/session/login", data={"password": "sevilla"})
        self.assertEqual(resp.status_code, 200)

        # Create first version of note
        resp = s.put(
            BASE_URL + "/notes/" + note_id, params={"timestamp": 1000}, data=note_text
        )
        self.assertEqual(resp.status_code, 200)

        # Read it back
        resp = s.get(BASE_URL + "/notes/" + note_id)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(note_text in resp.text)

        # Try updating it with an older timestamp
        resp = s.put(
            BASE_URL + "/notes/" + note_id, params={"timestamp": 500}, data="Testing"
        )
        self.assertEqual(resp.status_code, 200)

        # Read it back, shouldn't have changed
        resp = s.get(BASE_URL + "/notes/" + note_id)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(note_text in resp.text)

        note_text = "FoobarFoobar"

        # Actually update the note's text
        resp = s.put(
            BASE_URL + "/notes/" + note_id, params={"timestamp": 2000}, data=note_text
        )
        self.assertEqual(resp.status_code, 200)

        # Check new contents
        resp = s.get(BASE_URL + "/notes/" + note_id)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(note_text in resp.text)

        # Log out
        resp = s.post(BASE_URL + "/session/logout")
        self.assertEqual(resp.status_code, 200)

        # Try updating a note after logging out
        resp = s.put(
            BASE_URL + "/notes/" + note_id, params={"timestamp": 2}, data=note_text
        )
        self.assertEqual(resp.status_code, 401)
