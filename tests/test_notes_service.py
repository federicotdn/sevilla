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
            NotesService.upsert_note(
                NotesService.generate_note_id(), "Test", utils.now()
            )

        ids = set()

        for i in range(1, 1 + total_notes // page_size):
            pagination = NotesService.paginate_notes(page=i, page_size=page_size)
            self.assertLessEqual(len(pagination.items), page_size)
            self.assertGreater(len(pagination.items), 0)

            page_ids_set = {note.id for note in pagination.items}
            self.assertEqual(len(page_ids_set), len(pagination.items))

            previous_len = len(ids)
            ids |= page_ids_set

            self.assertEqual(len(ids), previous_len + len(page_ids_set))

    def test_pagination_hidden(self):
        NotesService.upsert_note(VALID_ID, "Test", utils.now())
        pagination = NotesService.paginate_notes(page=1)
        self.assertEqual(len(pagination.items), 1)

        NotesService.hide_note(VALID_ID)
        pagination = NotesService.paginate_notes(page=1)
        self.assertEqual(len(pagination.items), 0)

    def test_pretty_preview(self):
        notes_previews = [
            ("hello", "hello"),
            ("hello    ", "hello"),
            ("hello    \nfoobar", "hello"),
            ("   hello", "hello"),
            ("helloooooooooooooooo", "hellooooooooooo"),
            ("\nhello", "hello"),
            ("\n\n\nhello", "hello"),
            ("hello\nfoobar", "hello"),
            ("hello\nfooooooooooooooooo", "hello"),
            ("fooooooooooooooooo\nhello", "foooooooooooooo"),
            ("", ""),
        ]

        for note, preview in notes_previews:
            with self.subTest(note=note, preview=preview):
                note = NotesService.upsert_note(
                    NotesService.generate_note_id(), note, utils.now()
                )
                self.assertEqual(preview, note.preview(15))

    def test_read_note(self):
        note = NotesService.upsert_note(VALID_ID, "Test", utils.now())
        self.assertFalse(note.read)

        NotesService.mark_as_read(note)
        self.assertTrue(note.read)

    def test_upate_read_note(self):
        note = NotesService.upsert_note(VALID_ID, "Test", utils.now())
        self.assertFalse(note.read)

        NotesService.mark_as_read(note)
        self.assertTrue(note.read)

        note = NotesService.upsert_note(VALID_ID, "foobar", utils.now(1000))
        self.assertFalse(note.read)

    def test_notes_search(self):
        note_1_id = NotesService.generate_note_id()
        note_2_id = NotesService.generate_note_id()
        note_3_id = NotesService.generate_note_id()
        NotesService.upsert_note(note_1_id, "hello world", utils.now())
        NotesService.upsert_note(note_2_id, "hello there", utils.now(1))
        NotesService.upsert_note(note_3_id, "aaaaaaaaaa", utils.now(2))

        notes = NotesService.paginate_notes(1, query="hello world")
        self.assertEqual(notes.total, 1)
        self.assertEqual(notes.items[0].contents, "hello world")

        notes = NotesService.paginate_notes(1, query="hello")
        self.assertEqual(notes.total, 2)
        self.assertEqual(notes.items[1].contents, "hello world")
        self.assertEqual(notes.items[0].contents, "hello there")

        notes = NotesService.paginate_notes(1, query="aa")
        self.assertEqual(notes.total, 1)
        self.assertEqual(notes.items[0].contents, "aaaaaaaaaa")

        notes = NotesService.paginate_notes(1, query="foobarfoobar")
        self.assertEqual(notes.total, 0)
