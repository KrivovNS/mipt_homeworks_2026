from .chunk_mode import run_file_chunk_mode
from .config import load_config
from .console import ConsoleCommand, parse_command, print_start_menu
from .file_loader import insert_files_content
from .history import MessageHistory
from .llm_client import LLMClient
from .models import ChatMessage


def main() -> None:
    try:
        config = load_config()

    except ValueError as error:
        print(f'Config error: {error}')
        return

    llm_client = LLMClient(config)
    history = MessageHistory(config)

    print_start_menu()

    while True:
        user_input = input('>>> ').strip()

        if not user_input:
            continue

        command = parse_command(user_input)

        match command:
            case ConsoleCommand.EXIT:
                print('Bye!')
                break

            case ConsoleCommand.RESET:
                history.clear()
                print_start_menu()
                continue

            case ConsoleCommand.FILE_CHUNK:
                run_file_chunk_mode(user_input, llm_client)
                continue

            case _:
                prepared_input = insert_files_content(user_input)

                history.add_message(
                    ChatMessage(
                        role='user',
                        content=prepared_input,
                    )
                )

                messages = history.get_history_with_system_prompt(config.system_prompt)

                try:
                    answer = _print_streaming_answer(llm_client, messages)

                except KeyboardInterrupt:
                    print('\nRequest interrupted')
                    continue

                except Exception as error:
                    print(f'LLM error: {error}')
                    continue

                history.add_message(
                    ChatMessage(
                        role='assistant',
                        content=answer,
                    )
                )


def _print_streaming_answer(
    llm_client: LLMClient,
    messages: list[ChatMessage],
) -> str:
    answer_parts = []

    print()

    for part in llm_client.generate_stream(messages):
        print(part, end='', flush=True)
        answer_parts.append(part)

    print()
    print()

    return ''.join(answer_parts)


if __name__ == '__main__':
    main()
