from enum import Enum


class ConsoleCommand(Enum):
    EXIT = '\\q'
    RESET = '/reset'
    FILE_CHUNK = '/file_chunk'


def parse_command(text: str) -> ConsoleCommand | None:
    if text == ConsoleCommand.EXIT.value:
        return ConsoleCommand.EXIT

    if text == ConsoleCommand.RESET.value:
        return ConsoleCommand.RESET

    if text.startswith(ConsoleCommand.FILE_CHUNK.value):
        return ConsoleCommand.FILE_CHUNK

    return None


def print_start_menu() -> None:
    clear_screen()

    print('GigaVibeMIPTCode started')
    print('Commands:')
    print('\\q - exit')
    print('/reset - clear chat')
    print('/file_chunk - process large files in chunks')
    print()


def clear_screen() -> None:
    print('\033c', end='')
