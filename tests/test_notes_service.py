import random
from tests import BaseTest, utils
from sevilla.services import NotesService
from sevilla.exceptions import NoteNotFound

VALID_ID = "69ffae8c08a4fbebadece21021c38080"


class TestNotesService(BaseTest):
    def test_id_is_valid(self):
        ids = ["a" * 32, VALID_ID, "1" * 32]

        for i in ids:
            with self.subTest(i=i):
                self.assertTrue(NotesService.id_is_valid(i))

    def test_id_is_not_valid(self):
        ids = [
            "69ffae8c08a4fbebadece21021c380800",
            None,
            "hello",
            "123",
            "69ffae8c08a4fbebadece21021c3808",
        ]

        for i in ids:
            with self.subTest(i=i):
                self.assertFalse(NotesService.id_is_valid(i))

    def test_create_note(self):
        NotesService.upsert_note(VALID_ID, "Hello, world!", utils.now())
        note = NotesService.get_note(VALID_ID)
        self.assertEqual(note.id, VALID_ID)

    def test_update_note(self):
        with self.assertRaises(NoteNotFound):
            note = NotesService.get_note(VALID_ID)

        NotesService.upsert_note(VALID_ID, "Hello, world!", utils.now())
        NotesService.upsert_note(VALID_ID, "goodbye", utils.now())

        note = NotesService.get_note(VALID_ID)
        self.assertEqual(note.contents, "goodbye")

    def test_hide_note(self):
        NotesService.upsert_note(VALID_ID, "Hello, world!", utils.now())

        note = NotesService.get_note(VALID_ID)
        self.assertFalse(note.hidden)

        NotesService.hide_note(VALID_ID)
        note = NotesService.get_note(VALID_ID)
        self.assertTrue(note.hidden)

    def test_previews_pagination(self):
        total_notes = random.randint(20, 50)
        page_size = 15

        for _ in range(total_notes):
            NotesService.upsert_note(utils.generate_note_id(), "Test", utils.now())

        ids = set()

        for i in range(1, 1 + total_notes // page_size):
            pagination = NotesService.note_previews(page=i, page_size=page_size)
            self.assertLessEqual(len(pagination.items), page_size)
            self.assertGreater(len(pagination.items), 0)

            page_ids_set = {preview.id for preview in pagination.items}
            self.assertEqual(len(page_ids_set), len(pagination.items))

            previous_len = len(ids)
            ids |= page_ids_set

            self.assertEqual(len(ids), previous_len + len(page_ids_set))

    def test_pagination_hidden(self):
        NotesService.upsert_note(VALID_ID, "Test", utils.now())
        pagination = NotesService.note_previews(page=1)
        self.assertEqual(len(pagination.items), 1)

        NotesService.hide_note(VALID_ID)
        pagination = NotesService.note_previews(page=1)
        self.assertEqual(len(pagination.items), 0)

    def test_pretty_preview(self):
        notes_previews = [
            ("hello", "hello"),
            ("hello    ", "hello"),
            ("hello    \nfoobar", "hello..."),
            ("   hello", "hello"),
            ("helloooooooooooooooo", "hellooooooooooo..."),
            ("\nhello", "..."),
            ("\n\n\nhello", "..."),
            ("hello\nfoobar", "hello..."),
            ("hello\nfooooooooooooooooo", "hello..."),
            ("fooooooooooooooooo\nhello", "foooooooooooooo..."),
            ("", "..."),
        ]

        for note, preview in notes_previews:
            with self.subTest(note=note, preview=preview):
                self.assertEqual(preview, NotesService._pretty_preview(note, 15))
