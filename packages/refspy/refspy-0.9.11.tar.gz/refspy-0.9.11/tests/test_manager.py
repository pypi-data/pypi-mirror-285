import pytest
from context import *

from refspy import refspy
from refspy.book import Book
from refspy.languages.english import ENGLISH
from refspy.libraries.en_US import NT
from refspy.library import Library
from refspy.manager import Manager
from refspy.range import Range, range
from refspy.reference import Reference, reference, verse_reference
from refspy.verse import Verse, verse

BOOK = Book(id=2, name="Book", abbrev="Bk", aliases=["vol"], chapters=3)

LIBRARY = Library(id=1, name="Library", abbrev="Lib", books=[BOOK])

REFERENCES = [
    # 'Book 1:1–2' in Library
    reference(range(verse(LIBRARY.id, BOOK.id, 1, 1), verse(LIBRARY.id, BOOK.id, 1, 2)))
]

__ = Manager([LIBRARY], ENGLISH)
REFSPY = refspy()


def test_init():
    assert __.libraries[LIBRARY.id] == LIBRARY
    assert __.book_aliases["Book"] == (LIBRARY.id, BOOK.id)
    assert __.book_aliases["Bk"] == (LIBRARY.id, BOOK.id)


def test_make_hotspots():
    tuples = __.find_references("Book 1:2, 2:1, 3:4, 1:4-5, 7, 3:6")
    text = __.make_hotspots_text([ref for _, ref in tuples if ref], top=2, limit=10)
    assert text is not None
    assert "Bk 1 ❙❙❙" in text
    assert "Bk 3 ❙❙" in text


def test_make_hotspots_scaling():
    tuples = __.find_references("Book 1:2, 2:1, 3:4, 1:4-5, 7, 3:6, " * 100)
    text = __.make_hotspots_text([ref for _, ref in tuples if ref], top=2, limit=10)
    assert text is not None
    assert "Bk 1 ❙❙❙❙❙❙❙❙❙❙" in text
    assert "Bk 3 ❙❙❙❙❙❙❙" in text


def test_make_hotspots_empty():
    text = __.make_hotspots_text([], top=2, limit=10)
    assert text is None


def test_non_unique():
    """
    Repeating any name/alias values raise an error.
    """
    with pytest.raises(ValueError):
        _ = Manager([LIBRARY, LIBRARY], ENGLISH)


def test_sort_references():
    ref_1 = verse_reference(NT.id, 1, 2, 3)
    ref_2 = verse_reference(NT.id, 1, 2, 4)
    ref_3 = verse_reference(NT.id, 1, 2, 5)
    sorted_ref = __.sort_references([ref_3, ref_2, ref_1])
    assert sorted_ref.ranges == [ref_1.ranges[0], ref_2.ranges[0], ref_3.ranges[0]]


def test_merge_references():
    ref_1 = verse_reference(NT.id, 1, 2, 3)
    ref_2 = verse_reference(NT.id, 1, 2, 3, 4)
    ref_3 = verse_reference(NT.id, 1, 2, 4, 5)
    merged = __.merge_references([ref_3, ref_2, ref_1])
    assert len(merged.ranges) == 1
    assert merged == verse_reference(NT.id, 1, 2, 3, 5)


def test_combine_references():
    ref_1 = verse_reference(NT.id, 1, 2, 3)
    ref_2 = verse_reference(NT.id, 1, 2, 4)
    ref_3 = verse_reference(NT.id, 1, 2, 5, 6)
    combined = __.combine_references([ref_3, ref_2, ref_1])
    assert len(combined.ranges) == 1
    assert combined == verse_reference(NT.id, 1, 2, 3, 6)


def test_collate_by_id():
    collation = __.collate_by_id(REFERENCES)
    for library_id, book_collation in collation.items():
        assert library_id == LIBRARY.id
        for book_id, book_references in book_collation.items():
            assert book_id == BOOK.id
            assert book_references == REFERENCES


def test_collate():
    collation = __.collate(REFERENCES)
    for library, book_collation in collation:
        assert library == LIBRARY
        for book, book_references in book_collation:
            assert book == BOOK
            assert book_references == REFERENCES


def test_first_reference():
    text = "Book 1:1"
    _, reference = __.first_reference(text)
    assert reference is not None
    assert __.name(reference) == text


def test_find_references():
    tuples = __.find_references("Book 1:1–2:4")
    _, reference = tuples[0]
    assert reference is not None
    assert __.name(reference) == "Book 1:1–2:4"


def test_find_all():
    text = "Book 1:1, Book 2:2"
    tuples = list(__.find_references(text))
    assert tuples[0] == ("Book 1:1", __.r("Book 1:1"))
    assert tuples[1] == ("Book 2:2", __.r("Book 2:2"))


def test_next_chapter():
    __ = Manager([LIBRARY], ENGLISH)
    ch_1 = __.bcv("Book", 1)
    ch_2 = __.bcv("Book", 2)
    assert __.next_chapter(ch_1) == ch_2


def test_prev_chapter():
    __ = Manager([LIBRARY], ENGLISH)
    ch_2 = __.bcv("Book", 2)
    ch_1 = __.bcv("Book", 1)
    assert __.prev_chapter(ch_2) == ch_1


def test_bcv():
    bk = __.bcv("Book")
    assert __.name(bk) == "Book"
    bk_2 = __.bcv("Book", 2)
    assert __.name(bk_2) == "Book 2"
    bk_2_1 = __.bcv("Book", 2, 1)
    assert __.name(bk_2_1) == "Book 2:1"


def test_bcr():
    bk_2_135 = __.bcr("Book", 2, [1, 3, 5])
    assert __.name(bk_2_135) == "Book 2:1, 3, 5"
    bk_2_1357 = __.bcr("Book", 2, [(1, 3), (5, 7)])
    assert __.name(bk_2_1357) == "Book 2:1–3, 5–7"


def test_r():
    ref = __.r("Book 1:1")
    assert ref is not None
    assert __.name(ref) == "Book 1:1"
    ref = __.r("Book 1:1, 3")
    assert ref is not None
    assert __.name(ref) == "Book 1:1, 3"
    ref = __.r("Book 1:1-3")
    assert ref is not None
    assert __.name(ref) == "Book 1:1–3"
    ref = __.r("Book 1:1-3, 5-7")
    assert ref is not None
    assert __.name(ref) == "Book 1:1–3, 5–7"
    ref = __.r("Book 1:1–2:4")
    assert ref is not None
    assert __.name(ref) == "Book 1:1–2:4"
    ref = __.r("Book 1:1-2:4")
    assert ref is not None
    assert __.name(ref) == "Book 1:1–2:4"


def test_get_book():
    ref = __.r("Book 1:1")
    assert ref is not None
    book = __.get_book(ref)
    assert book.name == "Book"


def test_book_reference():
    ref = __.r("Book 1:1")
    assert ref is not None
    book_ref = __.book_reference(ref)
    assert __.name(book_ref) == "Book"


def test_chapter_reference():
    ref = __.r("Book 1:1")
    assert ref is not None
    chapter_ref = __.chapter_reference(ref)
    assert __.name(chapter_ref) == "Book 1"


def test_name():
    ref = __.r("Book 1:1")
    assert ref is not None
    assert __.name(ref) == "Book 1:1"


def test_book():
    ref = __.r("Book 1:1")
    assert ref is not None
    assert __.book(ref) == "Book"


def test_numbers():
    ref = __.r("Book 1:1")
    assert ref is not None
    assert __.numbers(ref) == "1:1"


def test_abbrev_name():
    ref = __.r("Book 1:1")
    assert ref is not None
    assert __.abbrev_name(ref) == "Bk 1:1"


def test_abbrev_book():
    ref = __.r("Book 1:1")
    assert ref is not None
    assert __.abbrev_book(ref) == "Bk"


def test_template():
    ref = __.r("1 Cor 2:3-4, 5")
    if ref is not None:
        assert __.template(ref, "x {NAME}") == "x 1 Corinthians 2:3–4, 5"
        assert __.template(ref, "x {BOOK}") == "x 1 Corinthians"
        assert __.template(ref, "x {NUMBERS}") == "x 2:3–4, 5"
        assert __.template(ref, "x {ABBREV_NAME}") == "x 1 Cor 2:3–4, 5"
        assert __.template(ref, "x {ABBREV_BOOK}") == "x 1 Cor"
        assert __.template(ref, "x {ABBREV_NUMBERS}") == "x 2:3–4, 5"
        assert __.template(ref, "x {ESC_NAME}") == "x 1%20Corinthians%202%3A3-4,%205"
        assert __.template(ref, "x {ESC_BOOK}") == "x 1%20Corinthians"
        assert __.template(ref, "x {ESC_NUMBERS}") == "x 2%3A3-4,%205"
        assert __.template(ref, "x {ESC_ABBREV_NAME}") == "x 1%20Cor%202%3A3-4,%205"
        assert __.template(ref, "x {ESC_ABBREV_BOOK}") == "x 1%20Cor"
        assert __.template(ref, "x {ESC_ABBREV_NUMBERS}") == "x 2%3A3-4,%205"
        assert __.template(ref, "x {PARAM_NAME}") == "x 1cor+2:3-4,+5"
        assert __.template(ref, "x {PARAM_BOOK}") == "x 1cor"
        assert __.template(ref, "x {PARAM_NUMBERS}") == "x 2:3-4,+5"


def test_bad():
    refs = [
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=1, verse=20),
                    end=Verse(library=200, book=20, chapter=1, verse=23),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=8, verse=1),
                    end=Verse(library=200, book=20, chapter=8, verse=36),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=23, verse=33),
                    end=Verse(library=200, book=20, chapter=23, verse=35),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=26, verse=13),
                    end=Verse(library=200, book=20, chapter=26, verse=14),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=26, verse=16),
                    end=Verse(library=200, book=20, chapter=26, verse=16),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=12, chapter=4, verse=2),
                    end=Verse(library=400, book=12, chapter=4, verse=2),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=14, chapter=3, verse=1),
                    end=Verse(library=400, book=14, chapter=3, verse=1),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=24, chapter=29, verse=7),
                    end=Verse(library=200, book=24, chapter=29, verse=7),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=21, chapter=1, verse=1),
                    end=Verse(library=400, book=21, chapter=1, verse=1),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=21, chapter=2, verse=11),
                    end=Verse(library=400, book=21, chapter=2, verse=18),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=11, chapter=3, verse=20),
                    end=Verse(library=400, book=11, chapter=3, verse=20),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=10, chapter=2, verse=19),
                    end=Verse(library=400, book=10, chapter=2, verse=19),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=8, chapter=5, verse=20),
                    end=Verse(library=400, book=8, chapter=5, verse=20),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=22, chapter=3, verse=13),
                    end=Verse(library=400, book=22, chapter=3, verse=13),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=19, chapter=11, verse=13),
                    end=Verse(library=400, book=19, chapter=11, verse=13),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=13, chapter=29, verse=14),
                    end=Verse(library=200, book=13, chapter=29, verse=15),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=19, chapter=12, verse=14),
                    end=Verse(library=400, book=19, chapter=12, verse=14),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=13, chapter=4, verse=11),
                    end=Verse(library=400, book=13, chapter=4, verse=11),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=9, chapter=5, verse=22),
                    end=Verse(library=400, book=9, chapter=5, verse=23),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=15, chapter=6, verse=11),
                    end=Verse(library=400, book=15, chapter=6, verse=11),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=20, chapter=3, verse=13),
                    end=Verse(library=400, book=20, chapter=3, verse=13),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=6, chapter=2, verse=4),
                    end=Verse(library=400, book=6, chapter=2, verse=4),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=8, chapter=6, verse=6),
                    end=Verse(library=400, book=8, chapter=6, verse=6),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=16, chapter=3, verse=10),
                    end=Verse(library=400, book=16, chapter=3, verse=10),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=15, chapter=3, verse=3),
                    end=Verse(library=400, book=15, chapter=3, verse=3),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=21, chapter=3, verse=4),
                    end=Verse(library=400, book=21, chapter=3, verse=4),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=17, chapter=3, verse=2),
                    end=Verse(library=400, book=17, chapter=3, verse=2),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=13, chapter=2, verse=7),
                    end=Verse(library=400, book=13, chapter=2, verse=8),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=8, chapter=1, verse=3),
                    end=Verse(library=400, book=8, chapter=1, verse=4),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=10, chapter=4, verse=32),
                    end=Verse(library=400, book=10, chapter=4, verse=32),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=1, chapter=18, verse=15),
                    end=Verse(library=400, book=1, chapter=18, verse=20),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=6, verse=1),
                    end=Verse(library=400, book=7, chapter=6, verse=8),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=10, chapter=4, verse=25),
                    end=Verse(library=400, book=10, chapter=5, verse=20),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=12, chapter=3, verse=1),
                    end=Verse(library=400, book=12, chapter=3, verse=18),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=19, chapter=15, verse=1),
                    end=Verse(library=200, book=19, chapter=15, verse=999),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=19, chapter=15, verse=1),
                    end=Verse(library=200, book=19, chapter=15, verse=5),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=12, chapter=3, verse=17),
                    end=Verse(library=400, book=12, chapter=3, verse=17),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=10, chapter=4, verse=30),
                    end=Verse(library=400, book=10, chapter=4, verse=30),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=20, chapter=3, verse=9),
                    end=Verse(library=400, book=20, chapter=3, verse=9),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=10, chapter=4, verse=25),
                    end=Verse(library=400, book=10, chapter=4, verse=25),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=12, chapter=3, verse=16),
                    end=Verse(library=400, book=12, chapter=3, verse=16),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=10, chapter=5, verse=16),
                    end=Verse(library=400, book=10, chapter=5, verse=17),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=10, chapter=4, verse=31),
                    end=Verse(library=400, book=10, chapter=4, verse=31),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=12, chapter=3, verse=8),
                    end=Verse(library=400, book=12, chapter=3, verse=8),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=20, chapter=1, verse=19),
                    end=Verse(library=400, book=20, chapter=1, verse=20),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=20, chapter=1, verse=26),
                    end=Verse(library=400, book=20, chapter=1, verse=26),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=10, chapter=4, verse=26),
                    end=Verse(library=400, book=10, chapter=4, verse=26),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=20, chapter=1, verse=19),
                    end=Verse(library=400, book=20, chapter=1, verse=19),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=12, chapter=3, verse=13),
                    end=Verse(library=400, book=12, chapter=3, verse=13),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=10, chapter=5, verse=2),
                    end=Verse(library=400, book=10, chapter=5, verse=2),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=12, chapter=3, verse=12),
                    end=Verse(library=400, book=12, chapter=3, verse=12),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=12, chapter=3, verse=14),
                    end=Verse(library=400, book=12, chapter=3, verse=14),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=20, chapter=3, verse=3),
                    end=Verse(library=400, book=20, chapter=3, verse=6),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=9, chapter=5, verse=15),
                    end=Verse(library=400, book=9, chapter=5, verse=15),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=10, chapter=4, verse=29),
                    end=Verse(library=400, book=10, chapter=4, verse=29),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=10, chapter=4, verse=1),
                    end=Verse(library=400, book=10, chapter=4, verse=999),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=10, chapter=4, verse=32),
                    end=Verse(library=400, book=10, chapter=4, verse=32),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=10, chapter=5, verse=1),
                    end=Verse(library=400, book=10, chapter=5, verse=2),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=10, chapter=5, verse=21),
                    end=Verse(library=400, book=10, chapter=5, verse=33),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=12, chapter=3, verse=1),
                    end=Verse(library=400, book=12, chapter=3, verse=11),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=12, chapter=3, verse=7),
                    end=Verse(library=400, book=12, chapter=3, verse=7),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=12, chapter=3, verse=6),
                    end=Verse(library=400, book=12, chapter=3, verse=6),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=12, chapter=3, verse=3),
                    end=Verse(library=400, book=12, chapter=3, verse=3),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=12, chapter=3, verse=10),
                    end=Verse(library=400, book=12, chapter=3, verse=10),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=12, chapter=3, verse=11),
                    end=Verse(library=400, book=12, chapter=3, verse=11),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=12, chapter=3, verse=1),
                    end=Verse(library=400, book=12, chapter=3, verse=2),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=12, chapter=3, verse=5),
                    end=Verse(library=400, book=12, chapter=3, verse=5),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=12, chapter=3, verse=15),
                    end=Verse(library=400, book=12, chapter=3, verse=15),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=12, chapter=3, verse=2),
                    end=Verse(library=400, book=12, chapter=3, verse=2),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=20, chapter=3, verse=8),
                    end=Verse(library=400, book=20, chapter=3, verse=10),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=1, chapter=1, verse=26),
                    end=Verse(library=200, book=1, chapter=1, verse=27),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=1, chapter=9, verse=6),
                    end=Verse(library=200, book=1, chapter=9, verse=6),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=1, chapter=25, verse=31),
                    end=Verse(library=400, book=1, chapter=25, verse=46),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=5, chapter=10, verse=17),
                    end=Verse(library=200, book=5, chapter=10, verse=17),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=14, chapter=19, verse=7),
                    end=Verse(library=200, book=14, chapter=19, verse=7),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=5, chapter=10, verse=34),
                    end=Verse(library=400, book=5, chapter=10, verse=34),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=6, chapter=2, verse=11),
                    end=Verse(library=400, book=6, chapter=2, verse=11),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=6, chapter=10, verse=12),
                    end=Verse(library=400, book=6, chapter=10, verse=12),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=9, chapter=2, verse=6),
                    end=Verse(library=400, book=9, chapter=2, verse=6),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=12, chapter=3, verse=25),
                    end=Verse(library=400, book=12, chapter=3, verse=25),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=10, chapter=6, verse=9),
                    end=Verse(library=400, book=10, chapter=6, verse=9),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=18, chapter=34, verse=19),
                    end=Verse(library=200, book=18, chapter=34, verse=19),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=5, chapter=24, verse=14),
                    end=Verse(library=200, book=5, chapter=24, verse=15),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=30, chapter=5, verse=10),
                    end=Verse(library=200, book=30, chapter=5, verse=13),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=30, chapter=8, verse=4),
                    end=Verse(library=200, book=30, chapter=8, verse=6),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=11, verse=20),
                    end=Verse(library=400, book=7, chapter=11, verse=22),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=3, chapter=19, verse=15),
                    end=Verse(library=200, book=3, chapter=19, verse=15),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=2, chapter=23, verse=1),
                    end=Verse(library=200, book=2, chapter=23, verse=8),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=20, chapter=2, verse=1),
                    end=Verse(library=400, book=20, chapter=2, verse=1),
                ),
                Range(
                    start=Verse(library=400, book=20, chapter=2, verse=8),
                    end=Verse(library=400, book=20, chapter=2, verse=9),
                ),
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=21, chapter=1, verse=17),
                    end=Verse(library=400, book=21, chapter=1, verse=17),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=11, verse=18),
                    end=Verse(library=400, book=7, chapter=11, verse=19),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=23, chapter=56, verse=3),
                    end=Verse(library=200, book=23, chapter=56, verse=8),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=30, chapter=4, verse=1),
                    end=Verse(library=200, book=30, chapter=5, verse=999),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=5, chapter=10, verse=1),
                    end=Verse(library=400, book=5, chapter=10, verse=999),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=18, verse=17),
                    end=Verse(library=200, book=20, chapter=18, verse=17),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=16, chapter=4, verse=3),
                    end=Verse(library=400, book=16, chapter=4, verse=3),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=13, verse=4),
                    end=Verse(library=400, book=7, chapter=13, verse=6),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=20, chapter=3, verse=13),
                    end=Verse(library=400, book=20, chapter=3, verse=13),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=11, chapter=2, verse=1),
                    end=Verse(library=400, book=11, chapter=2, verse=999),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=10, chapter=5, verse=11),
                    end=Verse(library=400, book=10, chapter=5, verse=11),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=6, chapter=12, verse=9),
                    end=Verse(library=400, book=6, chapter=12, verse=21),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=25, verse=21),
                    end=Verse(library=200, book=20, chapter=25, verse=22),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=6, chapter=12, verse=9),
                    end=Verse(library=400, book=6, chapter=12, verse=9),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=6, verse=1),
                    end=Verse(library=400, book=7, chapter=6, verse=9),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=1, verse=7),
                    end=Verse(library=200, book=20, chapter=1, verse=7),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=9, verse=10),
                    end=Verse(library=200, book=20, chapter=9, verse=10),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=19, chapter=111, verse=10),
                    end=Verse(library=200, book=19, chapter=111, verse=10),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=31, verse=10),
                    end=Verse(library=200, book=20, chapter=31, verse=31),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=10, chapter=20, verse=22),
                    end=Verse(library=200, book=10, chapter=20, verse=22),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=21, verse=22),
                    end=Verse(library=200, book=20, chapter=21, verse=22),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=21, chapter=9, verse=14),
                    end=Verse(library=200, book=21, chapter=9, verse=15),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=1, verse=2),
                    end=Verse(library=200, book=20, chapter=1, verse=6),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=2, verse=10),
                    end=Verse(library=200, book=20, chapter=2, verse=11),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=18, verse=15),
                    end=Verse(library=200, book=20, chapter=18, verse=15),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=3, chapter=22, verse=26),
                    end=Verse(library=400, book=3, chapter=22, verse=27),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=11, chapter=2, verse=3),
                    end=Verse(library=400, book=11, chapter=2, verse=7),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=12, chapter=3, verse=1),
                    end=Verse(library=400, book=12, chapter=3, verse=999),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=12, chapter=2, verse=18),
                    end=Verse(library=400, book=12, chapter=2, verse=18),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=6, chapter=2, verse=17),
                    end=Verse(library=400, book=6, chapter=2, verse=17),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=6, chapter=3, verse=27),
                    end=Verse(library=400, book=6, chapter=3, verse=27),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=6, chapter=4, verse=2),
                    end=Verse(library=400, book=6, chapter=4, verse=2),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=6, chapter=5, verse=1),
                    end=Verse(library=400, book=6, chapter=5, verse=11),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=6, chapter=11, verse=18),
                    end=Verse(library=400, book=6, chapter=11, verse=18),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=6, chapter=15, verse=17),
                    end=Verse(library=400, book=6, chapter=15, verse=17),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=8, verse=1),
                    end=Verse(library=400, book=7, chapter=8, verse=1),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=4, verse=6),
                    end=Verse(library=400, book=7, chapter=4, verse=6),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=4, verse=18),
                    end=Verse(library=400, book=7, chapter=4, verse=18),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=5, verse=2),
                    end=Verse(library=400, book=7, chapter=5, verse=2),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=13, verse=4),
                    end=Verse(library=400, book=7, chapter=13, verse=4),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=8, chapter=10, verse=1),
                    end=Verse(library=400, book=8, chapter=11, verse=999),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=8, chapter=11, verse=20),
                    end=Verse(library=400, book=8, chapter=11, verse=20),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=8, chapter=11, verse=16),
                    end=Verse(library=400, book=8, chapter=11, verse=33),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=8, chapter=12, verse=1),
                    end=Verse(library=400, book=8, chapter=12, verse=10),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=8, chapter=12, verse=16),
                    end=Verse(library=400, book=8, chapter=12, verse=33),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=8, chapter=11, verse=7),
                    end=Verse(library=400, book=8, chapter=11, verse=9),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=8, chapter=12, verse=13),
                    end=Verse(library=400, book=8, chapter=12, verse=13),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=8, chapter=11, verse=1),
                    end=Verse(library=400, book=8, chapter=12, verse=999),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=27, verse=2),
                    end=Verse(library=200, book=20, chapter=27, verse=2),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=3, chapter=19, verse=17),
                    end=Verse(library=200, book=3, chapter=19, verse=18),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=16, chapter=4, verse=2),
                    end=Verse(library=400, book=16, chapter=4, verse=2),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=12, chapter=1, verse=28),
                    end=Verse(library=400, book=12, chapter=1, verse=28),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=13, chapter=5, verse=14),
                    end=Verse(library=400, book=13, chapter=5, verse=14),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=10, verse=10),
                    end=Verse(library=200, book=20, chapter=10, verse=10),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=13, chapter=5, verse=12),
                    end=Verse(library=400, book=13, chapter=5, verse=12),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=1, chapter=18, verse=15),
                    end=Verse(library=400, book=1, chapter=18, verse=15),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=15, chapter=3, verse=16),
                    end=Verse(library=400, book=15, chapter=4, verse=2),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=15, chapter=5, verse=20),
                    end=Verse(library=400, book=15, chapter=5, verse=20),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=15, chapter=3, verse=10),
                    end=Verse(library=400, book=15, chapter=3, verse=11),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=1, chapter=19, verse=15),
                    end=Verse(library=400, book=1, chapter=19, verse=17),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=5, verse=1),
                    end=Verse(library=400, book=7, chapter=5, verse=2),
                ),
                Range(
                    start=Verse(library=400, book=7, chapter=5, verse=9),
                    end=Verse(library=400, book=7, chapter=5, verse=13),
                ),
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=1, chapter=12, verse=34),
                    end=Verse(library=400, book=1, chapter=12, verse=34),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=3, chapter=6, verse=45),
                    end=Verse(library=400, book=3, chapter=6, verse=45),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=19, chapter=11, verse=1),
                    end=Verse(library=400, book=19, chapter=11, verse=999),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=9, chapter=2, verse=16),
                    end=Verse(library=400, book=9, chapter=2, verse=16),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=1, chapter=23, verse=23),
                    end=Verse(library=400, book=1, chapter=23, verse=23),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=9, chapter=3, verse=1),
                    end=Verse(library=400, book=9, chapter=3, verse=999),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=11, verse=1),
                    end=Verse(library=400, book=7, chapter=11, verse=1),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=11, chapter=3, verse=17),
                    end=Verse(library=400, book=11, chapter=3, verse=17),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=3, chapter=6, verse=43),
                    end=Verse(library=400, book=3, chapter=6, verse=45),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=3, chapter=2, verse=19),
                    end=Verse(library=400, book=3, chapter=2, verse=19),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=2, chapter=7, verse=21),
                    end=Verse(library=400, book=2, chapter=7, verse=21),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=19, chapter=4, verse=12),
                    end=Verse(library=400, book=19, chapter=4, verse=12),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=4, verse=23),
                    end=Verse(library=200, book=20, chapter=4, verse=23),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=8, chapter=6, verse=11),
                    end=Verse(library=400, book=8, chapter=6, verse=13),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=23, chapter=3, verse=17),
                    end=Verse(library=400, book=23, chapter=3, verse=17),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=11, chapter=4, verse=8),
                    end=Verse(library=400, book=11, chapter=4, verse=8),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=2, chapter=12, verse=28),
                    end=Verse(library=400, book=2, chapter=12, verse=31),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=5, chapter=6, verse=5),
                    end=Verse(library=200, book=5, chapter=6, verse=5),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=3, chapter=19, verse=18),
                    end=Verse(library=200, book=3, chapter=19, verse=18),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=6, chapter=13, verse=9),
                    end=Verse(library=400, book=6, chapter=13, verse=10),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=9, chapter=5, verse=14),
                    end=Verse(library=400, book=9, chapter=5, verse=14),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=20, chapter=2, verse=8),
                    end=Verse(library=400, book=20, chapter=2, verse=8),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=20, chapter=2, verse=17),
                    end=Verse(library=400, book=20, chapter=2, verse=17),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=23, chapter=3, verse=18),
                    end=Verse(library=400, book=23, chapter=3, verse=18),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=1, chapter=25, verse=31),
                    end=Verse(library=400, book=1, chapter=25, verse=46),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=3, chapter=12, verse=1),
                    end=Verse(library=400, book=3, chapter=12, verse=3),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=1, chapter=12, verse=33),
                    end=Verse(library=400, book=1, chapter=12, verse=37),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=1, chapter=15, verse=10),
                    end=Verse(library=400, book=1, chapter=15, verse=20),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=20, chapter=1, verse=26),
                    end=Verse(library=400, book=20, chapter=1, verse=26),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=20, chapter=3, verse=8),
                    end=Verse(library=400, book=20, chapter=3, verse=8),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=31, verse=8),
                    end=Verse(library=200, book=20, chapter=31, verse=9),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=10, chapter=5, verse=11),
                    end=Verse(library=400, book=10, chapter=5, verse=11),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=3, chapter=5, verse=1),
                    end=Verse(library=200, book=3, chapter=5, verse=1),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=16, verse=28),
                    end=Verse(library=200, book=20, chapter=16, verse=28),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=20, chapter=1, verse=19),
                    end=Verse(library=400, book=20, chapter=1, verse=19),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=13, verse=2),
                    end=Verse(library=400, book=7, chapter=13, verse=2),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=1, chapter=18, verse=1),
                    end=Verse(library=400, book=1, chapter=18, verse=999),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=1, chapter=18, verse=15),
                    end=Verse(library=400, book=1, chapter=18, verse=15),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=23, chapter=5, verse=21),
                    end=Verse(library=200, book=23, chapter=5, verse=21),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=6, chapter=12, verse=3),
                    end=Verse(library=400, book=6, chapter=12, verse=3),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=16, chapter=2, verse=22),
                    end=Verse(library=400, book=16, chapter=2, verse=23),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=6, verse=19),
                    end=Verse(library=200, book=20, chapter=6, verse=19),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=3, chapter=1, verse=52),
                    end=Verse(library=400, book=3, chapter=1, verse=52),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=1, chapter=15, verse=18),
                    end=Verse(library=400, book=1, chapter=15, verse=20),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=2, chapter=7, verse=21),
                    end=Verse(library=400, book=2, chapter=7, verse=23),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=10, chapter=4, verse=31),
                    end=Verse(library=400, book=10, chapter=4, verse=31),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=12, chapter=3, verse=8),
                    end=Verse(library=400, book=12, chapter=3, verse=8),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=21, chapter=2, verse=1),
                    end=Verse(library=400, book=21, chapter=2, verse=1),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=20, chapter=2, verse=4),
                    end=Verse(library=400, book=20, chapter=2, verse=4),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=6, verse=5),
                    end=Verse(library=200, book=20, chapter=6, verse=5),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=18, verse=8),
                    end=Verse(library=200, book=20, chapter=18, verse=8),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=26, verse=22),
                    end=Verse(library=200, book=20, chapter=26, verse=22),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=16, chapter=4, verse=3),
                    end=Verse(library=400, book=16, chapter=4, verse=3),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=6, chapter=12, verse=16),
                    end=Verse(library=400, book=6, chapter=12, verse=16),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=18, verse=17),
                    end=Verse(library=200, book=20, chapter=18, verse=17),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=4, chapter=13, verse=35),
                    end=Verse(library=400, book=4, chapter=13, verse=35),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=4, chapter=15, verse=13),
                    end=Verse(library=400, book=4, chapter=15, verse=13),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=15, chapter=5, verse=8),
                    end=Verse(library=400, book=15, chapter=5, verse=8),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=5, chapter=10, verse=19),
                    end=Verse(library=200, book=5, chapter=10, verse=19),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=1, chapter=5, verse=43),
                    end=Verse(library=400, book=1, chapter=5, verse=48),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=3, chapter=6, verse=32),
                    end=Verse(library=400, book=3, chapter=6, verse=36),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=3, chapter=10, verse=29),
                    end=Verse(library=400, book=3, chapter=10, verse=37),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=4, chapter=4, verse=9),
                    end=Verse(library=400, book=4, chapter=4, verse=9),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=3, chapter=19, verse=1),
                    end=Verse(library=200, book=3, chapter=19, verse=999),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=3, chapter=19, verse=34),
                    end=Verse(library=200, book=3, chapter=19, verse=34),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=3, chapter=15, verse=4),
                    end=Verse(library=400, book=3, chapter=15, verse=4),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=9, verse=26),
                    end=Verse(library=400, book=7, chapter=9, verse=26),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=3, chapter=10, verse=29),
                    end=Verse(library=400, book=3, chapter=10, verse=29),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=4, chapter=13, verse=34),
                    end=Verse(library=400, book=4, chapter=13, verse=34),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=10, chapter=5, verse=25),
                    end=Verse(library=400, book=10, chapter=5, verse=25),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=3, chapter=4, verse=10),
                    end=Verse(library=200, book=3, chapter=4, verse=11),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=6, chapter=5, verse=7),
                    end=Verse(library=400, book=6, chapter=5, verse=8),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=23, chapter=4, verse=8),
                    end=Verse(library=400, book=23, chapter=4, verse=8),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=23, chapter=4, verse=20),
                    end=Verse(library=400, book=23, chapter=4, verse=20),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=13, verse=1),
                    end=Verse(library=400, book=7, chapter=13, verse=3),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=1, chapter=28, verse=19),
                    end=Verse(library=400, book=1, chapter=28, verse=20),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=3, chapter=6, verse=40),
                    end=Verse(library=400, book=3, chapter=6, verse=40),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=8, chapter=5, verse=17),
                    end=Verse(library=400, book=8, chapter=5, verse=20),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=11, chapter=1, verse=27),
                    end=Verse(library=400, book=11, chapter=1, verse=27),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=21, chapter=2, verse=5),
                    end=Verse(library=400, book=21, chapter=2, verse=5),
                ),
                Range(
                    start=Verse(library=400, book=21, chapter=2, verse=9),
                    end=Verse(library=400, book=21, chapter=2, verse=9),
                ),
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=8, chapter=2, verse=15),
                    end=Verse(library=400, book=8, chapter=2, verse=17),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=8, chapter=3, verse=3),
                    end=Verse(library=400, book=8, chapter=3, verse=3),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=10, chapter=5, verse=1),
                    end=Verse(library=400, book=10, chapter=5, verse=1),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=12, chapter=1, verse=15),
                    end=Verse(library=400, book=12, chapter=1, verse=15),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=19, chapter=1, verse=3),
                    end=Verse(library=400, book=19, chapter=1, verse=3),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=4, chapter=1, verse=14),
                    end=Verse(library=400, book=4, chapter=1, verse=14),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=4, chapter=14, verse=9),
                    end=Verse(library=400, book=4, chapter=14, verse=9),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=6, chapter=8, verse=29),
                    end=Verse(library=400, book=6, chapter=8, verse=29),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=15, verse=49),
                    end=Verse(library=400, book=7, chapter=15, verse=49),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=8, chapter=3, verse=18),
                    end=Verse(library=400, book=8, chapter=3, verse=18),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=11, verse=1),
                    end=Verse(library=400, book=7, chapter=11, verse=1),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=10, chapter=4, verse=30),
                    end=Verse(library=400, book=10, chapter=4, verse=30),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=9, chapter=5, verse=22),
                    end=Verse(library=400, book=9, chapter=5, verse=23),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=6, chapter=2, verse=24),
                    end=Verse(library=400, book=6, chapter=2, verse=24),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=23, chapter=52, verse=5),
                    end=Verse(library=200, book=23, chapter=52, verse=5),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=26, chapter=36, verse=20),
                    end=Verse(library=200, book=26, chapter=36, verse=20),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=12, chapter=3, verse=17),
                    end=Verse(library=400, book=12, chapter=3, verse=17),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=11, chapter=4, verse=4),
                    end=Verse(library=400, book=11, chapter=4, verse=4),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=6, chapter=5, verse=3),
                    end=Verse(library=400, book=6, chapter=5, verse=5),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=20, chapter=1, verse=2),
                    end=Verse(library=400, book=20, chapter=1, verse=4),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=21, chapter=3, verse=14),
                    end=Verse(library=400, book=21, chapter=3, verse=14),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=9, chapter=21, verse=15),
                    end=Verse(library=200, book=9, chapter=21, verse=15),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=7, chapter=3, verse=1),
                    end=Verse(library=200, book=7, chapter=3, verse=999),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=11, chapter=18, verse=27),
                    end=Verse(library=200, book=11, chapter=18, verse=27),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=23, chapter=44, verse=9),
                    end=Verse(library=200, book=23, chapter=44, verse=20),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=22, verse=13),
                    end=Verse(library=200, book=20, chapter=22, verse=13),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=26, verse=13),
                    end=Verse(library=200, book=20, chapter=26, verse=13),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=23, verse=34),
                    end=Verse(library=200, book=20, chapter=23, verse=35),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=1, chapter=23, verse=24),
                    end=Verse(library=400, book=1, chapter=23, verse=24),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=8, chapter=11, verse=1),
                    end=Verse(library=400, book=8, chapter=12, verse=999),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=11, verse=8),
                    end=Verse(library=400, book=7, chapter=11, verse=9),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=9, chapter=5, verse=12),
                    end=Verse(library=400, book=9, chapter=5, verse=12),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=10, chapter=5, verse=4),
                    end=Verse(library=400, book=10, chapter=5, verse=4),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=6, chapter=12, verse=15),
                    end=Verse(library=400, book=6, chapter=12, verse=15),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=1, chapter=3, verse=1),
                    end=Verse(library=200, book=1, chapter=3, verse=7),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=2, chapter=20, verse=7),
                    end=Verse(library=200, book=2, chapter=20, verse=7),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=27, chapter=21, verse=27),
                    end=Verse(library=400, book=27, chapter=21, verse=27),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=27, chapter=22, verse=25),
                    end=Verse(library=400, book=27, chapter=22, verse=25),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=4, chapter=8, verse=44),
                    end=Verse(library=400, book=4, chapter=8, verse=44),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=2, chapter=20, verse=16),
                    end=Verse(library=200, book=2, chapter=20, verse=16),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=2, chapter=23, verse=1),
                    end=Verse(library=200, book=2, chapter=23, verse=1),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=3, chapter=19, verse=11),
                    end=Verse(library=200, book=3, chapter=19, verse=12),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=1, chapter=15, verse=18),
                    end=Verse(library=400, book=1, chapter=15, verse=20),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=2, chapter=7, verse=21),
                    end=Verse(library=400, book=2, chapter=7, verse=23),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=10, chapter=4, verse=31),
                    end=Verse(library=400, book=10, chapter=4, verse=31),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=12, chapter=3, verse=8),
                    end=Verse(library=400, book=12, chapter=3, verse=8),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=21, chapter=2, verse=1),
                    end=Verse(library=400, book=21, chapter=2, verse=1),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=6, chapter=1, verse=29),
                    end=Verse(library=400, book=6, chapter=1, verse=29),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=8, chapter=12, verse=20),
                    end=Verse(library=400, book=8, chapter=12, verse=20),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=10, chapter=4, verse=25),
                    end=Verse(library=400, book=10, chapter=4, verse=25),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=12, chapter=3, verse=9),
                    end=Verse(library=400, book=12, chapter=3, verse=9),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=8, chapter=4, verse=2),
                    end=Verse(library=400, book=8, chapter=4, verse=2),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=19, chapter=34, verse=12),
                    end=Verse(library=200, book=19, chapter=34, verse=13),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=21, chapter=3, verse=10),
                    end=Verse(library=400, book=21, chapter=3, verse=10),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=24, chapter=17, verse=9),
                    end=Verse(library=200, book=24, chapter=17, verse=9),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=9, verse=8),
                    end=Verse(library=200, book=20, chapter=9, verse=8),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=17, verse=10),
                    end=Verse(library=200, book=20, chapter=17, verse=10),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=1, chapter=5, verse=37),
                    end=Verse(library=400, book=1, chapter=5, verse=37),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=1, chapter=5, verse=33),
                    end=Verse(library=400, book=1, chapter=5, verse=37),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=20, chapter=5, verse=12),
                    end=Verse(library=400, book=20, chapter=5, verse=12),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=1, chapter=5, verse=1),
                    end=Verse(library=400, book=1, chapter=5, verse=999),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=3, chapter=5, verse=1),
                    end=Verse(library=200, book=3, chapter=5, verse=1),
                ),
                Range(
                    start=Verse(library=200, book=3, chapter=5, verse=5),
                    end=Verse(library=200, book=3, chapter=5, verse=5),
                ),
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=20, verse=10),
                    end=Verse(library=200, book=20, chapter=20, verse=10),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=3, chapter=19, verse=35),
                    end=Verse(library=200, book=3, chapter=19, verse=35),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=5, chapter=25, verse=13),
                    end=Verse(library=200, book=5, chapter=25, verse=16),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=3, chapter=6, verse=2),
                    end=Verse(library=200, book=3, chapter=6, verse=5),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=5, chapter=19, verse=18),
                    end=Verse(library=200, book=5, chapter=19, verse=19),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=19, chapter=101, verse=7),
                    end=Verse(library=200, book=19, chapter=101, verse=7),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=19, chapter=119, verse=66),
                    end=Verse(library=200, book=19, chapter=119, verse=66),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=8, chapter=11, verse=23),
                    end=Verse(library=400, book=8, chapter=11, verse=27),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=1, chapter=5, verse=11),
                    end=Verse(library=400, book=1, chapter=5, verse=12),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=21, chapter=2, verse=18),
                    end=Verse(library=400, book=21, chapter=3, verse=7),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=21, chapter=3, verse=15),
                    end=Verse(library=400, book=21, chapter=3, verse=16),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=4, chapter=15, verse=25),
                    end=Verse(library=400, book=4, chapter=15, verse=25),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=21, chapter=3, verse=1),
                    end=Verse(library=400, book=21, chapter=3, verse=999),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=13, verse=7),
                    end=Verse(library=400, book=7, chapter=13, verse=7),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=20, chapter=1, verse=19),
                    end=Verse(library=400, book=20, chapter=1, verse=20),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=20, chapter=3, verse=5),
                    end=Verse(library=400, book=20, chapter=3, verse=6),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=20, chapter=3, verse=8),
                    end=Verse(library=400, book=20, chapter=3, verse=9),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=1, chapter=5, verse=38),
                    end=Verse(library=400, book=1, chapter=5, verse=41),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=6, chapter=12, verse=17),
                    end=Verse(library=400, book=6, chapter=12, verse=21),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=4, verse=12),
                    end=Verse(library=400, book=7, chapter=4, verse=13),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=13, chapter=5, verse=15),
                    end=Verse(library=400, book=13, chapter=5, verse=15),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=21, chapter=3, verse=9),
                    end=Verse(library=400, book=21, chapter=3, verse=9),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=6, chapter=12, verse=17),
                    end=Verse(library=400, book=6, chapter=12, verse=17),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=6, verse=7),
                    end=Verse(library=400, book=7, chapter=6, verse=9),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=10, chapter=4, verse=28),
                    end=Verse(library=400, book=10, chapter=4, verse=28),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=10, chapter=5, verse=4),
                    end=Verse(library=400, book=10, chapter=5, verse=4),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=12, chapter=3, verse=8),
                    end=Verse(library=400, book=12, chapter=3, verse=8),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=1, chapter=21, verse=28),
                    end=Verse(library=400, book=1, chapter=21, verse=32),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=5, verse=9),
                    end=Verse(library=400, book=7, chapter=5, verse=11),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=2, chapter=2, verse=17),
                    end=Verse(library=400, book=2, chapter=2, verse=17),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=1, chapter=9, verse=12),
                    end=Verse(library=400, book=1, chapter=9, verse=12),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=3, chapter=5, verse=31),
                    end=Verse(library=400, book=3, chapter=5, verse=31),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=8, chapter=6, verse=18),
                    end=Verse(library=400, book=8, chapter=7, verse=1),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=8, chapter=6, verse=14),
                    end=Verse(library=400, book=8, chapter=6, verse=16),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=3, chapter=19, verse=19),
                    end=Verse(library=200, book=3, chapter=19, verse=19),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=5, chapter=22, verse=10),
                    end=Verse(library=200, book=5, chapter=22, verse=10),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=3, chapter=26, verse=11),
                    end=Verse(library=200, book=3, chapter=26, verse=12),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=26, chapter=37, verse=27),
                    end=Verse(library=200, book=26, chapter=37, verse=27),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=23, chapter=52, verse=11),
                    end=Verse(library=200, book=23, chapter=52, verse=11),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=10, chapter=7, verse=14),
                    end=Verse(library=200, book=10, chapter=7, verse=14),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=23, chapter=43, verse=6),
                    end=Verse(library=200, book=23, chapter=43, verse=6),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=3, chapter=5, verse=2),
                    end=Verse(library=200, book=3, chapter=5, verse=2),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=3, chapter=7, verse=21),
                    end=Verse(library=200, book=3, chapter=7, verse=21),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=8, chapter=7, verse=1),
                    end=Verse(library=400, book=8, chapter=7, verse=1),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=6, verse=18),
                    end=Verse(library=400, book=7, chapter=6, verse=18),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=10, verse=14),
                    end=Verse(library=400, book=7, chapter=10, verse=14),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=5, chapter=15, verse=19),
                    end=Verse(library=400, book=5, chapter=15, verse=20),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=6, chapter=14, verse=14),
                    end=Verse(library=400, book=6, chapter=14, verse=14),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=14, chapter=29, verse=16),
                    end=Verse(library=200, book=14, chapter=29, verse=16),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=23, chapter=64, verse=6),
                    end=Verse(library=200, book=23, chapter=64, verse=6),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=23, chapter=8, verse=10),
                    end=Verse(library=200, book=23, chapter=8, verse=10),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=23, chapter=35, verse=17),
                    end=Verse(library=200, book=23, chapter=35, verse=17),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=23, chapter=2, verse=15),
                    end=Verse(library=400, book=23, chapter=2, verse=16),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=20, chapter=4, verse=4),
                    end=Verse(library=400, book=20, chapter=4, verse=4),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=20, chapter=4, verse=1),
                    end=Verse(library=400, book=20, chapter=4, verse=8),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=4, chapter=3, verse=16),
                    end=Verse(library=400, book=4, chapter=3, verse=16),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=23, chapter=2, verse=16),
                    end=Verse(library=400, book=23, chapter=2, verse=16),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=2, chapter=4, verse=19),
                    end=Verse(library=400, book=2, chapter=4, verse=19),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=1, chapter=13, verse=22),
                    end=Verse(library=400, book=1, chapter=13, verse=22),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=1, chapter=6, verse=24),
                    end=Verse(library=400, book=1, chapter=6, verse=24),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=1, chapter=5, verse=14),
                    end=Verse(library=400, book=1, chapter=5, verse=14),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=4, chapter=5, verse=13),
                    end=Verse(library=400, book=4, chapter=5, verse=13),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=4, chapter=17, verse=14),
                    end=Verse(library=400, book=4, chapter=17, verse=18),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=1, chapter=18, verse=1),
                    end=Verse(library=400, book=1, chapter=18, verse=999),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=1, chapter=6, verse=5),
                    end=Verse(library=400, book=1, chapter=6, verse=5),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=1, chapter=23, verse=1),
                    end=Verse(library=400, book=1, chapter=23, verse=999),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=1, chapter=23, verse=17),
                    end=Verse(library=400, book=1, chapter=23, verse=17),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=1, chapter=23, verse=27),
                    end=Verse(library=400, book=1, chapter=23, verse=27),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=5, chapter=13, verse=9),
                    end=Verse(library=400, book=5, chapter=13, verse=10),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=30, chapter=4, verse=1),
                    end=Verse(library=200, book=30, chapter=4, verse=1),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=26, chapter=13, verse=4),
                    end=Verse(library=200, book=26, chapter=13, verse=4),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=3, chapter=6, verse=28),
                    end=Verse(library=400, book=3, chapter=6, verse=28),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=6, chapter=12, verse=14),
                    end=Verse(library=400, book=6, chapter=12, verse=14),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=20, chapter=3, verse=10),
                    end=Verse(library=400, book=20, chapter=3, verse=10),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=1, chapter=5, verse=1),
                    end=Verse(library=400, book=1, chapter=5, verse=999),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=1, chapter=5, verse=21),
                    end=Verse(library=400, book=1, chapter=5, verse=25),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=1, chapter=5, verse=25),
                    end=Verse(library=400, book=1, chapter=5, verse=25),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=19, chapter=4, verse=4),
                    end=Verse(library=200, book=19, chapter=4, verse=4),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=1, chapter=6, verse=12),
                    end=Verse(library=400, book=1, chapter=6, verse=12),
                ),
                Range(
                    start=Verse(library=400, book=1, chapter=6, verse=14),
                    end=Verse(library=400, book=1, chapter=6, verse=15),
                ),
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=2, chapter=11, verse=25),
                    end=Verse(library=400, book=2, chapter=11, verse=25),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=3, chapter=17, verse=3),
                    end=Verse(library=400, book=3, chapter=17, verse=4),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=10, chapter=4, verse=26),
                    end=Verse(library=400, book=10, chapter=4, verse=26),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=6, chapter=12, verse=14),
                    end=Verse(library=400, book=6, chapter=12, verse=21),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=4, verse=12),
                    end=Verse(library=400, book=7, chapter=4, verse=13),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=21, chapter=2, verse=23),
                    end=Verse(library=400, book=21, chapter=2, verse=23),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=21, chapter=3, verse=9),
                    end=Verse(library=400, book=21, chapter=3, verse=9),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=19, chapter=12, verse=14),
                    end=Verse(library=400, book=19, chapter=12, verse=15),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=9, chapter=5, verse=14),
                    end=Verse(library=400, book=9, chapter=5, verse=15),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=6, chapter=1, verse=29),
                    end=Verse(library=400, book=6, chapter=1, verse=31),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=5, verse=8),
                    end=Verse(library=400, book=7, chapter=5, verse=8),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=10, chapter=4, verse=31),
                    end=Verse(library=400, book=10, chapter=4, verse=31),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=12, chapter=3, verse=8),
                    end=Verse(library=400, book=12, chapter=3, verse=8),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=17, chapter=3, verse=3),
                    end=Verse(library=400, book=17, chapter=3, verse=3),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=21, chapter=2, verse=2),
                    end=Verse(library=400, book=21, chapter=2, verse=2),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=9, chapter=6, verse=1),
                    end=Verse(library=400, book=9, chapter=6, verse=1),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=21, chapter=2, verse=20),
                    end=Verse(library=400, book=21, chapter=2, verse=23),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=9, chapter=5, verse=14),
                    end=Verse(library=400, book=9, chapter=5, verse=15),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=21, chapter=3, verse=1),
                    end=Verse(library=400, book=21, chapter=3, verse=999),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=5, chapter=11, verse=18),
                    end=Verse(library=200, book=5, chapter=11, verse=20),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=6, chapter=1, verse=8),
                    end=Verse(library=200, book=6, chapter=1, verse=8),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=19, chapter=1, verse=2),
                    end=Verse(library=200, book=19, chapter=1, verse=2),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=19, chapter=119, verse=1),
                    end=Verse(library=200, book=19, chapter=119, verse=16),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=15, chapter=4, verse=13),
                    end=Verse(library=400, book=15, chapter=4, verse=13),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=16, chapter=2, verse=15),
                    end=Verse(library=400, book=16, chapter=2, verse=15),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=16, chapter=3, verse=16),
                    end=Verse(library=400, book=16, chapter=3, verse=16),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=11, chapter=3, verse=7),
                    end=Verse(library=400, book=11, chapter=3, verse=11),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=12, chapter=1, verse=9),
                    end=Verse(library=400, book=12, chapter=1, verse=10),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=11, chapter=1, verse=9),
                    end=Verse(library=400, book=11, chapter=1, verse=11),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=26, verse=3),
                    end=Verse(library=200, book=20, chapter=26, verse=3),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=18, chapter=11, verse=3),
                    end=Verse(library=200, book=18, chapter=11, verse=3),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=18, chapter=42, verse=7),
                    end=Verse(library=200, book=18, chapter=42, verse=9),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=9, verse=13),
                    end=Verse(library=200, book=20, chapter=9, verse=13),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=15, verse=7),
                    end=Verse(library=200, book=20, chapter=15, verse=7),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=1, verse=7),
                    end=Verse(library=200, book=20, chapter=1, verse=7),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=14, verse=33),
                    end=Verse(library=200, book=20, chapter=14, verse=33),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=15, verse=2),
                    end=Verse(library=200, book=20, chapter=15, verse=2),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=17, verse=24),
                    end=Verse(library=200, book=20, chapter=17, verse=24),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=12, verse=15),
                    end=Verse(library=200, book=20, chapter=12, verse=15),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=17, verse=16),
                    end=Verse(library=200, book=20, chapter=17, verse=16),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=10, verse=8),
                    end=Verse(library=200, book=20, chapter=10, verse=8),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=12, verse=23),
                    end=Verse(library=200, book=20, chapter=12, verse=23),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=18, verse=2),
                    end=Verse(library=200, book=20, chapter=18, verse=2),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=17, verse=28),
                    end=Verse(library=200, book=20, chapter=17, verse=28),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=14, verse=16),
                    end=Verse(library=200, book=20, chapter=14, verse=16),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=15, verse=5),
                    end=Verse(library=200, book=20, chapter=15, verse=5),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=21, verse=20),
                    end=Verse(library=200, book=20, chapter=21, verse=20),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=12, verse=16),
                    end=Verse(library=200, book=20, chapter=12, verse=16),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=14, verse=17),
                    end=Verse(library=200, book=20, chapter=14, verse=17),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=29, verse=11),
                    end=Verse(library=200, book=20, chapter=29, verse=11),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=20, verse=3),
                    end=Verse(library=200, book=20, chapter=20, verse=3),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=1, verse=32),
                    end=Verse(library=200, book=20, chapter=1, verse=32),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=3, verse=35),
                    end=Verse(library=200, book=20, chapter=3, verse=35),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=10, verse=21),
                    end=Verse(library=200, book=20, chapter=10, verse=21),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=11, verse=29),
                    end=Verse(library=200, book=20, chapter=11, verse=29),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=13, verse=20),
                    end=Verse(library=200, book=20, chapter=13, verse=20),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=14, verse=1),
                    end=Verse(library=200, book=20, chapter=14, verse=1),
                ),
                Range(
                    start=Verse(library=200, book=20, chapter=14, verse=3),
                    end=Verse(library=200, book=20, chapter=14, verse=3),
                ),
                Range(
                    start=Verse(library=200, book=20, chapter=14, verse=8),
                    end=Verse(library=200, book=20, chapter=14, verse=8),
                ),
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=16, verse=22),
                    end=Verse(library=200, book=20, chapter=16, verse=22),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=18, verse=6),
                    end=Verse(library=200, book=20, chapter=18, verse=7),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=19, verse=29),
                    end=Verse(library=200, book=20, chapter=19, verse=29),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=28, verse=26),
                    end=Verse(library=200, book=20, chapter=28, verse=26),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=10, verse=1),
                    end=Verse(library=200, book=20, chapter=10, verse=1),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=17, verse=21),
                    end=Verse(library=200, book=20, chapter=17, verse=21),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=26, verse=6),
                    end=Verse(library=200, book=20, chapter=26, verse=6),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=13, verse=19),
                    end=Verse(library=200, book=20, chapter=13, verse=19),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=10, verse=23),
                    end=Verse(library=200, book=20, chapter=10, verse=23),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=9, verse=8),
                    end=Verse(library=200, book=20, chapter=9, verse=8),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=17, verse=10),
                    end=Verse(library=200, book=20, chapter=17, verse=10),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=27, verse=22),
                    end=Verse(library=200, book=20, chapter=27, verse=22),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=19, chapter=14, verse=1),
                    end=Verse(library=200, book=19, chapter=14, verse=1),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=19, chapter=53, verse=1),
                    end=Verse(library=200, book=19, chapter=53, verse=1),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=26, verse=16),
                    end=Verse(library=200, book=20, chapter=26, verse=16),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=3, verse=7),
                    end=Verse(library=200, book=20, chapter=3, verse=7),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=26, verse=12),
                    end=Verse(library=200, book=20, chapter=26, verse=12),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=26, verse=5),
                    end=Verse(library=200, book=20, chapter=26, verse=5),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=26, verse=4),
                    end=Verse(library=200, book=20, chapter=26, verse=4),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=14, verse=7),
                    end=Verse(library=200, book=20, chapter=14, verse=7),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=23, verse=9),
                    end=Verse(library=200, book=20, chapter=23, verse=9),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=1, chapter=18, verse=15),
                    end=Verse(library=400, book=1, chapter=18, verse=17),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=15, chapter=6, verse=3),
                    end=Verse(library=400, book=15, chapter=6, verse=5),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=18, verse=17),
                    end=Verse(library=200, book=20, chapter=18, verse=17),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=6, chapter=12, verse=16),
                    end=Verse(library=400, book=6, chapter=12, verse=16),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=2, verse=1),
                    end=Verse(library=400, book=7, chapter=2, verse=5),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=5, chapter=17, verse=4),
                    end=Verse(library=400, book=5, chapter=17, verse=4),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=5, chapter=19, verse=26),
                    end=Verse(library=400, book=5, chapter=19, verse=26),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=5, chapter=28, verse=28),
                    end=Verse(library=400, book=5, chapter=28, verse=28),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=5, chapter=18, verse=4),
                    end=Verse(library=400, book=5, chapter=18, verse=4),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=5, verse=18),
                    end=Verse(library=400, book=7, chapter=5, verse=18),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=5, verse=11),
                    end=Verse(library=400, book=7, chapter=5, verse=11),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=2, verse=1),
                    end=Verse(library=400, book=7, chapter=2, verse=999),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=1, verse=10),
                    end=Verse(library=400, book=7, chapter=1, verse=17),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=3, verse=1),
                    end=Verse(library=400, book=7, chapter=4, verse=7),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=1, verse=18),
                    end=Verse(library=400, book=7, chapter=2, verse=16),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=4, verse=6),
                    end=Verse(library=400, book=7, chapter=4, verse=6),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=4, verse=14),
                    end=Verse(library=400, book=7, chapter=4, verse=21),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=4, verse=8),
                    end=Verse(library=400, book=7, chapter=4, verse=13),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=8, chapter=5, verse=12),
                    end=Verse(library=400, book=8, chapter=5, verse=12),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=8, chapter=10, verse=6),
                    end=Verse(library=400, book=8, chapter=10, verse=6),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=8, chapter=10, verse=12),
                    end=Verse(library=400, book=8, chapter=10, verse=18),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=8, chapter=10, verse=1),
                    end=Verse(library=400, book=8, chapter=10, verse=1),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=8, chapter=11, verse=1),
                    end=Verse(library=400, book=8, chapter=12, verse=999),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=9, chapter=1, verse=10),
                    end=Verse(library=400, book=9, chapter=1, verse=10),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=13, chapter=2, verse=4),
                    end=Verse(library=400, book=13, chapter=2, verse=6),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=1, verse=1),
                    end=Verse(library=400, book=7, chapter=3, verse=999),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=18, chapter=28, verse=28),
                    end=Verse(library=200, book=18, chapter=28, verse=28),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=5, chapter=10, verse=12),
                    end=Verse(library=200, book=5, chapter=10, verse=12),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=19, chapter=118, verse=6),
                    end=Verse(library=200, book=19, chapter=118, verse=6),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=19, chapter=34, verse=4),
                    end=Verse(library=200, book=19, chapter=34, verse=4),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=1, chapter=10, verse=28),
                    end=Verse(library=400, book=1, chapter=10, verse=28),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=29, verse=25),
                    end=Verse(library=200, book=20, chapter=29, verse=25),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=19, verse=23),
                    end=Verse(library=200, book=20, chapter=19, verse=23),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=27, chapter=2, verse=10),
                    end=Verse(library=400, book=27, chapter=2, verse=10),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=19, chapter=56, verse=1),
                    end=Verse(library=200, book=19, chapter=56, verse=999),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=8, chapter=11, verse=23),
                    end=Verse(library=400, book=8, chapter=11, verse=28),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=3, chapter=4, verse=30),
                    end=Verse(library=400, book=3, chapter=4, verse=30),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=5, chapter=9, verse=23),
                    end=Verse(library=400, book=5, chapter=9, verse=23),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=2, verse=3),
                    end=Verse(library=400, book=7, chapter=2, verse=3),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=8, chapter=7, verse=5),
                    end=Verse(library=400, book=8, chapter=7, verse=5),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=23, chapter=8, verse=12),
                    end=Verse(library=200, book=23, chapter=8, verse=13),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=23, chapter=4, verse=18),
                    end=Verse(library=400, book=23, chapter=4, verse=18),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=6, chapter=8, verse=15),
                    end=Verse(library=400, book=6, chapter=8, verse=15),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=19, chapter=2, verse=15),
                    end=Verse(library=400, book=19, chapter=2, verse=15),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=11, chapter=4, verse=6),
                    end=Verse(library=400, book=11, chapter=4, verse=7),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=21, chapter=3, verse=1),
                    end=Verse(library=400, book=21, chapter=3, verse=999),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=21, chapter=3, verse=6),
                    end=Verse(library=400, book=21, chapter=3, verse=6),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=5, chapter=7, verse=52),
                    end=Verse(library=400, book=5, chapter=7, verse=52),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=4, chapter=15, verse=20),
                    end=Verse(library=400, book=4, chapter=15, verse=20),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=16, chapter=3, verse=12),
                    end=Verse(library=400, book=16, chapter=3, verse=12),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=21, chapter=3, verse=14),
                    end=Verse(library=400, book=21, chapter=3, verse=14),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=4, chapter=7, verse=24),
                    end=Verse(library=400, book=4, chapter=7, verse=24),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=5, verse=12),
                    end=Verse(library=400, book=7, chapter=5, verse=13),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=6, verse=1),
                    end=Verse(library=400, book=7, chapter=6, verse=5),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=1, chapter=7, verse=1),
                    end=Verse(library=400, book=1, chapter=7, verse=1),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=3, chapter=6, verse=37),
                    end=Verse(library=400, book=3, chapter=6, verse=37),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=6, chapter=14, verse=4),
                    end=Verse(library=400, book=6, chapter=14, verse=4),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=20, chapter=4, verse=12),
                    end=Verse(library=400, book=20, chapter=4, verse=12),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=1, chapter=7, verse=1),
                    end=Verse(library=400, book=1, chapter=7, verse=5),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=3, chapter=6, verse=35),
                    end=Verse(library=400, book=3, chapter=6, verse=38),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=6, chapter=14, verse=1),
                    end=Verse(library=400, book=6, chapter=14, verse=4),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=20, chapter=2, verse=4),
                    end=Verse(library=400, book=20, chapter=2, verse=4),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=20, chapter=4, verse=11),
                    end=Verse(library=400, book=20, chapter=4, verse=12),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=6, chapter=12, verse=1),
                    end=Verse(library=400, book=6, chapter=14, verse=999),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=1, chapter=21, verse=12),
                    end=Verse(library=400, book=1, chapter=21, verse=13),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=24, chapter=7, verse=11),
                    end=Verse(library=200, book=24, chapter=7, verse=11),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=23, chapter=56, verse=6),
                    end=Verse(library=200, book=23, chapter=56, verse=8),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=1, chapter=23, verse=1),
                    end=Verse(library=400, book=1, chapter=23, verse=999),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=21, chapter=7, verse=9),
                    end=Verse(library=200, book=21, chapter=7, verse=9),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=20, chapter=1, verse=20),
                    end=Verse(library=400, book=20, chapter=1, verse=20),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=22, verse=14),
                    end=Verse(library=200, book=20, chapter=22, verse=15),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=30, verse=33),
                    end=Verse(library=200, book=20, chapter=30, verse=33),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=20, chapter=1, verse=19),
                    end=Verse(library=400, book=20, chapter=1, verse=20),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=14, verse=23),
                    end=Verse(library=200, book=20, chapter=14, verse=23),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=19, chapter=86, verse=15),
                    end=Verse(library=200, book=19, chapter=86, verse=15),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=2, chapter=34, verse=6),
                    end=Verse(library=200, book=2, chapter=34, verse=6),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=4, chapter=14, verse=18),
                    end=Verse(library=200, book=4, chapter=14, verse=18),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=16, chapter=9, verse=17),
                    end=Verse(library=200, book=16, chapter=9, verse=17),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=19, chapter=103, verse=8),
                    end=Verse(library=200, book=19, chapter=103, verse=8),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=19, chapter=145, verse=8),
                    end=Verse(library=200, book=19, chapter=145, verse=8),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=29, chapter=2, verse=13),
                    end=Verse(library=200, book=29, chapter=2, verse=13),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=32, chapter=4, verse=2),
                    end=Verse(library=200, book=32, chapter=4, verse=2),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=10, chapter=4, verse=26),
                    end=Verse(library=400, book=10, chapter=4, verse=27),
                ),
                Range(
                    start=Verse(library=400, book=10, chapter=4, verse=31),
                    end=Verse(library=400, book=10, chapter=4, verse=32),
                ),
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=13, chapter=4, verse=10),
                    end=Verse(library=400, book=13, chapter=4, verse=12),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=15, chapter=2, verse=1),
                    end=Verse(library=400, book=15, chapter=2, verse=2),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=6, chapter=13, verse=1),
                    end=Verse(library=400, book=6, chapter=13, verse=7),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=6, chapter=13, verse=4),
                    end=Verse(library=400, book=6, chapter=13, verse=4),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=6, chapter=12, verse=17),
                    end=Verse(library=400, book=6, chapter=12, verse=21),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=17, chapter=2, verse=5),
                    end=Verse(library=400, book=17, chapter=2, verse=5),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=17, chapter=2, verse=6),
                    end=Verse(library=400, book=17, chapter=2, verse=8),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=17, chapter=2, verse=10),
                    end=Verse(library=400, book=17, chapter=2, verse=10),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=13, chapter=4, verse=12),
                    end=Verse(library=400, book=13, chapter=4, verse=12),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=12, chapter=4, verse=5),
                    end=Verse(library=400, book=12, chapter=4, verse=5),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=15, chapter=3, verse=2),
                    end=Verse(library=400, book=15, chapter=3, verse=2),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=5, chapter=1, verse=13),
                    end=Verse(library=200, book=5, chapter=1, verse=13),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=8, chapter=4, verse=2),
                    end=Verse(library=400, book=8, chapter=4, verse=2),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=21, chapter=2, verse=12),
                    end=Verse(library=400, book=21, chapter=2, verse=12),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=21, chapter=3, verse=16),
                    end=Verse(library=400, book=21, chapter=3, verse=16),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=5, chapter=24, verse=16),
                    end=Verse(library=400, book=5, chapter=24, verse=16),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=6, chapter=12, verse=17),
                    end=Verse(library=400, book=6, chapter=12, verse=17),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=6, chapter=2, verse=1),
                    end=Verse(library=400, book=6, chapter=2, verse=999),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=23, chapter=52, verse=5),
                    end=Verse(library=200, book=23, chapter=52, verse=5),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=23, chapter=36, verse=20),
                    end=Verse(library=200, book=23, chapter=36, verse=20),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=6, chapter=2, verse=11),
                    end=Verse(library=400, book=6, chapter=2, verse=11),
                ),
                Range(
                    start=Verse(library=400, book=6, chapter=2, verse=23),
                    end=Verse(library=400, book=6, chapter=2, verse=24),
                ),
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=19, chapter=69, verse=6),
                    end=Verse(library=200, book=19, chapter=69, verse=6),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=5, chapter=5, verse=29),
                    end=Verse(library=400, book=5, chapter=5, verse=29),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=20, chapter=1, verse=19),
                    end=Verse(library=400, book=20, chapter=1, verse=20),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=20, chapter=1, verse=1),
                    end=Verse(library=400, book=20, chapter=1, verse=999),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=18, verse=13),
                    end=Verse(library=200, book=20, chapter=18, verse=13),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=5, verse=8),
                    end=Verse(library=400, book=7, chapter=5, verse=8),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=8, chapter=1, verse=12),
                    end=Verse(library=400, book=8, chapter=1, verse=12),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=8, chapter=2, verse=17),
                    end=Verse(library=400, book=8, chapter=2, verse=17),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=17, chapter=2, verse=7),
                    end=Verse(library=400, book=17, chapter=2, verse=8),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=17, chapter=2, verse=2),
                    end=Verse(library=400, book=17, chapter=2, verse=2),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=15, chapter=3, verse=8),
                    end=Verse(library=400, book=15, chapter=3, verse=8),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=26, verse=18),
                    end=Verse(library=200, book=20, chapter=26, verse=19),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=11, chapter=4, verse=4),
                    end=Verse(library=400, book=11, chapter=4, verse=4),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=13, chapter=5, verse=16),
                    end=Verse(library=400, book=13, chapter=5, verse=16),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=5, chapter=9, verse=4),
                    end=Verse(library=400, book=5, chapter=9, verse=4),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=9, chapter=2, verse=13),
                    end=Verse(library=400, book=9, chapter=2, verse=14),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=6, chapter=10, verse=2),
                    end=Verse(library=400, book=6, chapter=10, verse=2),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=19, verse=2),
                    end=Verse(library=200, book=20, chapter=19, verse=2),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=9, chapter=4, verse=18),
                    end=Verse(library=400, book=9, chapter=4, verse=18),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=10, chapter=4, verse=15),
                    end=Verse(library=400, book=10, chapter=4, verse=15),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=10, chapter=4, verse=25),
                    end=Verse(library=400, book=10, chapter=4, verse=25),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=19, chapter=19, verse=12),
                    end=Verse(library=200, book=19, chapter=19, verse=12),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=1, chapter=7, verse=12),
                    end=Verse(library=400, book=1, chapter=7, verse=12),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=2, chapter=12, verse=31),
                    end=Verse(library=400, book=2, chapter=12, verse=31),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=3, chapter=6, verse=31),
                    end=Verse(library=400, book=3, chapter=6, verse=31),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=3, chapter=10, verse=36),
                    end=Verse(library=400, book=3, chapter=10, verse=37),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=10, chapter=5, verse=28),
                    end=Verse(library=400, book=10, chapter=5, verse=30),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=4, chapter=15, verse=12),
                    end=Verse(library=400, book=4, chapter=15, verse=13),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=19, chapter=1, verse=1),
                    end=Verse(library=200, book=19, chapter=1, verse=1),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=1, verse=22),
                    end=Verse(library=200, book=20, chapter=1, verse=22),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=24, verse=9),
                    end=Verse(library=200, book=20, chapter=24, verse=9),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=13, verse=1),
                    end=Verse(library=200, book=20, chapter=13, verse=1),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=15, verse=12),
                    end=Verse(library=200, book=20, chapter=15, verse=12),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=21, verse=24),
                    end=Verse(library=200, book=20, chapter=21, verse=24),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=3, verse=34),
                    end=Verse(library=200, book=20, chapter=3, verse=34),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=14, verse=6),
                    end=Verse(library=200, book=20, chapter=14, verse=6),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=9, verse=7),
                    end=Verse(library=200, book=20, chapter=9, verse=7),
                ),
                Range(
                    start=Verse(library=200, book=20, chapter=9, verse=8),
                    end=Verse(library=200, book=20, chapter=9, verse=8),
                ),
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=22, verse=10),
                    end=Verse(library=200, book=20, chapter=22, verse=10),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=29, verse=8),
                    end=Verse(library=200, book=20, chapter=29, verse=8),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=11, chapter=18, verse=25),
                    end=Verse(library=200, book=11, chapter=18, verse=27),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=23, verse=34),
                    end=Verse(library=200, book=20, chapter=23, verse=35),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=26, verse=1),
                    end=Verse(library=200, book=20, chapter=26, verse=1),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=23, chapter=44, verse=9),
                    end=Verse(library=200, book=23, chapter=44, verse=20),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=19, chapter=2, verse=4),
                    end=Verse(library=200, book=19, chapter=2, verse=4),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=19, verse=25),
                    end=Verse(library=200, book=20, chapter=19, verse=25),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=21, verse=11),
                    end=Verse(library=200, book=20, chapter=21, verse=11),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=6, chapter=14, verse=15),
                    end=Verse(library=400, book=6, chapter=14, verse=15),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=8, verse=1),
                    end=Verse(library=400, book=7, chapter=8, verse=999),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=6, chapter=14, verse=2),
                    end=Verse(library=400, book=6, chapter=14, verse=2),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=6, chapter=14, verse=5),
                    end=Verse(library=400, book=6, chapter=14, verse=5),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=9, chapter=4, verse=10),
                    end=Verse(library=400, book=9, chapter=4, verse=10),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=8, verse=9),
                    end=Verse(library=400, book=7, chapter=8, verse=11),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=10, verse=27),
                    end=Verse(library=400, book=7, chapter=10, verse=29),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=14, verse=6),
                    end=Verse(library=400, book=7, chapter=14, verse=6),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=9, chapter=5, verse=1),
                    end=Verse(library=400, book=9, chapter=5, verse=999),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=12, chapter=2, verse=1),
                    end=Verse(library=400, book=12, chapter=2, verse=999),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=12, chapter=2, verse=16),
                    end=Verse(library=400, book=12, chapter=2, verse=16),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=6, chapter=2, verse=15),
                    end=Verse(library=400, book=6, chapter=2, verse=15),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=15, chapter=1, verse=19),
                    end=Verse(library=400, book=15, chapter=1, verse=19),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=5, chapter=23, verse=1),
                    end=Verse(library=400, book=5, chapter=23, verse=1),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=5, chapter=24, verse=6),
                    end=Verse(library=400, book=5, chapter=24, verse=6),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=8, chapter=1, verse=12),
                    end=Verse(library=400, book=8, chapter=1, verse=12),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=19, chapter=9, verse=9),
                    end=Verse(library=400, book=19, chapter=9, verse=9),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=19, chapter=9, verse=14),
                    end=Verse(library=400, book=19, chapter=9, verse=14),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=15, chapter=4, verse=2),
                    end=Verse(library=400, book=15, chapter=4, verse=2),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=17, chapter=1, verse=15),
                    end=Verse(library=400, book=17, chapter=1, verse=15),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=19, chapter=10, verse=22),
                    end=Verse(library=400, book=19, chapter=10, verse=22),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=10, verse=27),
                    end=Verse(library=400, book=7, chapter=10, verse=27),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=6, chapter=9, verse=1),
                    end=Verse(library=400, book=6, chapter=9, verse=1),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=15, chapter=1, verse=5),
                    end=Verse(library=400, book=15, chapter=1, verse=5),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=12, chapter=4, verse=2),
                    end=Verse(library=400, book=12, chapter=4, verse=2),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=14, chapter=3, verse=1),
                    end=Verse(library=400, book=14, chapter=3, verse=1),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=10, chapter=6, verse=19),
                    end=Verse(library=400, book=10, chapter=6, verse=20),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=12, chapter=4, verse=3),
                    end=Verse(library=400, book=12, chapter=4, verse=4),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=10, chapter=1, verse=18),
                    end=Verse(library=400, book=10, chapter=1, verse=18),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=12, chapter=1, verse=9),
                    end=Verse(library=400, book=12, chapter=1, verse=9),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=6, chapter=1, verse=1),
                    end=Verse(library=400, book=6, chapter=1, verse=999),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=5, chapter=13, verse=13),
                    end=Verse(library=400, book=5, chapter=13, verse=52),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=5, chapter=17, verse=16),
                    end=Verse(library=400, book=5, chapter=17, verse=34),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=5, chapter=14, verse=14),
                    end=Verse(library=400, book=5, chapter=14, verse=18),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=5, chapter=18, verse=4),
                    end=Verse(library=400, book=5, chapter=18, verse=4),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=5, chapter=17, verse=4),
                    end=Verse(library=400, book=5, chapter=17, verse=4),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=5, chapter=18, verse=13),
                    end=Verse(library=400, book=5, chapter=18, verse=13),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=5, chapter=19, verse=8),
                    end=Verse(library=400, book=5, chapter=19, verse=10),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=5, verse=11),
                    end=Verse(library=400, book=7, chapter=5, verse=11),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=28, verse=1),
                    end=Verse(library=200, book=20, chapter=28, verse=1),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=5, chapter=31, verse=6),
                    end=Verse(library=200, book=5, chapter=31, verse=6),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=5, chapter=4, verse=31),
                    end=Verse(library=400, book=5, chapter=4, verse=31),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=21, verse=29),
                    end=Verse(library=200, book=20, chapter=21, verse=29),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=10, chapter=3, verse=12),
                    end=Verse(library=400, book=10, chapter=3, verse=12),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=8, chapter=3, verse=12),
                    end=Verse(library=400, book=8, chapter=3, verse=13),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=10, chapter=4, verse=1),
                    end=Verse(library=400, book=10, chapter=4, verse=5),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=10, chapter=4, verse=1),
                    end=Verse(library=400, book=10, chapter=4, verse=999),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=10, chapter=4, verse=25),
                    end=Verse(library=400, book=10, chapter=4, verse=32),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=1, verse=10),
                    end=Verse(library=400, book=7, chapter=1, verse=10),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=12, chapter=3, verse=13),
                    end=Verse(library=400, book=12, chapter=3, verse=14),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=21, chapter=2, verse=1),
                    end=Verse(library=400, book=21, chapter=2, verse=1),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=12, chapter=3, verse=8),
                    end=Verse(library=400, book=12, chapter=3, verse=8),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=15, chapter=5, verse=13),
                    end=Verse(library=400, book=15, chapter=5, verse=13),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=14, chapter=3, verse=11),
                    end=Verse(library=400, book=14, chapter=3, verse=11),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=11, verse=13),
                    end=Verse(library=200, book=20, chapter=11, verse=13),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=20, verse=19),
                    end=Verse(library=200, book=20, chapter=20, verse=19),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=16, verse=28),
                    end=Verse(library=200, book=20, chapter=16, verse=28),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=26, verse=20),
                    end=Verse(library=200, book=20, chapter=26, verse=20),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=18, verse=8),
                    end=Verse(library=200, book=20, chapter=18, verse=8),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=26, verse=22),
                    end=Verse(library=200, book=20, chapter=26, verse=22),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=17, verse=4),
                    end=Verse(library=200, book=20, chapter=17, verse=4),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=8, chapter=13, verse=11),
                    end=Verse(library=400, book=8, chapter=13, verse=11),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=11, chapter=2, verse=2),
                    end=Verse(library=400, book=11, chapter=2, verse=2),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=11, chapter=4, verse=2),
                    end=Verse(library=400, book=11, chapter=4, verse=2),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=8, verse=5),
                    end=Verse(library=200, book=20, chapter=8, verse=5),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=1, verse=32),
                    end=Verse(library=200, book=20, chapter=1, verse=32),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=20, chapter=14, verse=15),
                    end=Verse(library=200, book=20, chapter=14, verse=15),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=1, chapter=7, verse=24),
                    end=Verse(library=400, book=1, chapter=7, verse=27),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=1, chapter=24, verse=45),
                    end=Verse(library=400, book=1, chapter=24, verse=51),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=1, chapter=25, verse=1),
                    end=Verse(library=400, book=1, chapter=25, verse=13),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=13, verse=10),
                    end=Verse(library=400, book=7, chapter=13, verse=10),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=14, verse=20),
                    end=Verse(library=400, book=7, chapter=14, verse=20),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=2, chapter=10, verse=14),
                    end=Verse(library=400, book=2, chapter=10, verse=14),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=1, chapter=18, verse=2),
                    end=Verse(library=400, book=1, chapter=18, verse=5),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=22, chapter=1, verse=5),
                    end=Verse(library=400, book=22, chapter=1, verse=8),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=3, verse=2),
                    end=Verse(library=400, book=7, chapter=3, verse=2),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=19, chapter=5, verse=12),
                    end=Verse(library=400, book=19, chapter=5, verse=12),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=19, chapter=5, verse=14),
                    end=Verse(library=400, book=19, chapter=5, verse=14),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=20, chapter=1, verse=4),
                    end=Verse(library=400, book=20, chapter=1, verse=4),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=12, chapter=2, verse=1),
                    end=Verse(library=400, book=12, chapter=2, verse=999),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=9, chapter=4, verse=8),
                    end=Verse(library=400, book=9, chapter=4, verse=9),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=12, chapter=1, verse=24),
                    end=Verse(library=400, book=12, chapter=2, verse=23),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=12, chapter=1, verse=28),
                    end=Verse(library=400, book=12, chapter=1, verse=28),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=10, chapter=4, verse=14),
                    end=Verse(library=400, book=10, chapter=4, verse=14),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=16, chapter=2, verse=22),
                    end=Verse(library=400, book=16, chapter=2, verse=23),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=17, chapter=3, verse=9),
                    end=Verse(library=400, book=17, chapter=3, verse=9),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=15, chapter=6, verse=3),
                    end=Verse(library=400, book=15, chapter=6, verse=5),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=6, chapter=12, verse=3),
                    end=Verse(library=400, book=6, chapter=12, verse=3),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=8, verse=1),
                    end=Verse(library=400, book=7, chapter=8, verse=1),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=200, book=24, chapter=9, verse=23),
                    end=Verse(library=200, book=24, chapter=9, verse=24),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=20, chapter=3, verse=1),
                    end=Verse(library=400, book=20, chapter=3, verse=1),
                )
            ]
        ),
        Reference(
            ranges=[
                Range(
                    start=Verse(library=400, book=7, chapter=1, verse=26),
                    end=Verse(library=400, book=7, chapter=1, verse=29),
                )
            ]
        ),
    ]
    text = REFSPY.make_hotspots_text(refs, 5, 10)
    assert text is not None
    assert "Col 3" in text
    assert "Eph 4" in text
    assert "Jam 1" in text
