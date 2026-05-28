from pathlib import Path

from pytest import MonkeyPatch

from src.main.file_loader import insert_files_content


def test_insert_files_content_replaces_file_reference(tmp_path: Path) -> None:
    file_path = tmp_path / 'example.txt'
    file_path.write_text('file content', encoding='utf-8')

    result = insert_files_content(f'Check this @::{file_path}::')

    assert 'Check this' in result
    assert 'file content' in result
    assert '@::' not in result


def test_insert_files_content_handles_missing_file() -> None:
    result = insert_files_content('Read @::missing.txt::')

    assert '[File not found:' in result


def test_insert_files_content_leaves_text_without_files() -> None:
    result = insert_files_content('ordinary message')

    assert result == 'ordinary message'


def test_insert_files_content_rejects_directory(tmp_path: Path) -> None:
    result = insert_files_content(f'Read @::{tmp_path}::')

    assert '[Path is not a file:' in result


def test_insert_files_content_rejects_large_file(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    import src.main.file_loader as file_loader

    file_path = tmp_path / 'big.txt'
    file_path.write_text('content', encoding='utf-8')

    monkeypatch.setattr(file_loader, 'MAX_FILE_SIZE_BYTES', 1)

    result = insert_files_content(f'Read @::{file_path}::')

    assert '[File is too large:' in result
