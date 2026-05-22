from src.main.console import ConsoleCommand, parse_command


def test_parse_exit_command() -> None:
    assert parse_command('\\q') == ConsoleCommand.EXIT


def test_parse_reset_command() -> None:
    assert parse_command('/reset') == ConsoleCommand.RESET


def test_parse_file_chunk_command() -> None:
    assert parse_command('/file_chunk paragraph=3 -y') == ConsoleCommand.FILE_CHUNK


def test_parse_unknown_command() -> None:
    assert parse_command('hello') is None