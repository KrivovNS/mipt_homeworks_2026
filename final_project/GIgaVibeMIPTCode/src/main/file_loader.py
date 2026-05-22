import re
from pathlib import Path

MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024
FILE_PATTERN = re.compile(r"@::(.+?)::")


def insert_files_content(user_text: str) -> str:
    return FILE_PATTERN.sub(_replace_file_reference, user_text)


def _replace_file_reference(match: re.Match[str]) -> str:
    file_path = Path(match.group(1))

    try:
        if not file_path.exists():
            return f"\n[File not found: {file_path}]\n"

        if not file_path.is_file():
            return f"\n[Path is not a file: {file_path}]\n"

        if file_path.stat().st_size > MAX_FILE_SIZE_BYTES:
            return f"\n[File is too large: {file_path}]\n"

        return "\n" + file_path.read_text(encoding="utf-8") + "\n"

    except UnicodeDecodeError:
        return f"\n[File is not a valid text file: {file_path}]\n"

    except OSError as error:
        return f"\n[Could not read file {file_path}: {error}]\n"