from src.main.chunk_mode import (
    extract_positive_int,
    make_chunks,
    split_by_length,
    split_by_paragraphs,
)


def test_extract_positive_int() -> None:
    assert extract_positive_int('/file_chunk paragraph=3', 'paragraph=', 1) == 3


def test_extract_positive_int_returns_default_for_bad_value() -> None:
    assert extract_positive_int('/file_chunk paragraph=bad', 'paragraph=', 1) == 1


def test_split_by_length() -> None:
    assert split_by_length('abcdef', 2) == ['ab', 'cd', 'ef']


def test_split_by_paragraphs() -> None:
    text = 'one\n\ntwo\nthree'

    assert split_by_paragraphs(text, 2) == ['one\ntwo', 'three']


def test_make_chunks_by_length() -> None:
    assert make_chunks('/file_chunk len=3', 'abcdef') == ['abc', 'def']


def test_make_chunks_by_paragraph_count() -> None:
    text = 'one\ntwo\nthree'

    assert make_chunks('/file_chunk paragraph=2', text) == ['one\ntwo', 'three']
