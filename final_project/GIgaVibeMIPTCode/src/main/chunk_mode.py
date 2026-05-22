from pathlib import Path

from .llm_client import LLMClient
from .models import ChatMessage

DEFAULT_PARAGRAPH_COUNT = 1
DEFAULT_CHUNK_LENGTH = 1000


def run_file_chunk_mode(command_text: str, llm_client: LLMClient) -> None:
    file_path = input('Введите путь до файла\n>>> ').strip()

    if file_path == '\\q':
        return

    user_prompt = input('Что нужно сделать для каждого фрагмента?\n>>> ').strip()

    if user_prompt == '\\q':
        return

    try:
        text = normalize_path(file_path).read_text(encoding='utf-8')

    except OSError as error:
        print(f'Could not read file: {error}')
        return

    except UnicodeDecodeError:
        print('File is not a valid text file')
        return

    chunks = make_chunks(command_text, text)
    auto_mode = '-y' in command_text

    print('Принято. Начинаю обработку:')

    for chunk in chunks:
        messages = [
            ChatMessage(
                role='user',
                content=f'{user_prompt}\n\nТекст фрагмента:\n{chunk}',
            )
        ]

        try:
            _print_streaming_chunk_answer(llm_client, messages)

        except KeyboardInterrupt:
            print('\nRequest interrupted')
            return

        if not auto_mode:
            next_input = input('Нажмите Enter для следующего фрагмента...')

            if next_input.strip() == '\\q':
                return

    print('Обработка файла завершена.')

def normalize_path(raw_path: str) -> Path:
    return Path(raw_path.strip().strip('"').strip("'"))

def _print_streaming_chunk_answer(llm_client: LLMClient, messages: list[ChatMessage]) -> None:
    print()

    for part in llm_client.generate_stream(messages):
        print(part, end='', flush=True)

    print()
    print()


def make_chunks(command_text: str, text: str) -> list[str]:
    if 'len=' in command_text:
        chunk_length = extract_positive_int(command_text,'len=', DEFAULT_CHUNK_LENGTH)

        return split_by_length(text, chunk_length)

    paragraph_count = extract_positive_int(command_text,'paragraph=', DEFAULT_PARAGRAPH_COUNT)

    return split_by_paragraphs(text, paragraph_count)


def extract_positive_int(text: str, prefix: str, default: int) -> int:
    for word in text.split():
        if word.startswith(prefix):
            value = word.removeprefix(prefix)

            if value.isdigit() and int(value) > 0:
                return int(value)

    return default


def split_by_length(text: str, chunk_length: int) -> list[str]:
    return [
        text[index:index + chunk_length]
        for index in range(0, len(text), chunk_length)
        if text[index:index + chunk_length].strip()
    ]


def split_by_paragraphs(text: str, paragraph_count: int) -> list[str]:
    paragraphs = [paragraph.strip() for paragraph in text.split('\n') if paragraph.strip()]

    chunks = []

    for index in range(0, len(paragraphs), paragraph_count):
        chunk = '\n'.join(paragraphs[index:index + paragraph_count])
        chunks.append(chunk)

    return chunks