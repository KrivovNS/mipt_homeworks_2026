from typing import Any, Iterator, cast

from pytest import CaptureFixture, MonkeyPatch

from src.main.llm_client import LLMClient
from src.main.models import ChatMessage


def test_print_streaming_answer(capsys: CaptureFixture[str]) -> None:
    from src.main.main import _print_streaming_answer

    class FakeClient:
        def generate_stream(self, messages: list[ChatMessage]) -> Iterator[str]:
            yield 'Hello'
            yield ', '
            yield 'world'

    answer = _print_streaming_answer(
        cast(LLMClient, FakeClient()),
        [ChatMessage(role='user', content='hi')],
    )

    captured = capsys.readouterr()

    assert answer == 'Hello, world'
    assert 'Hello, world' in captured.out


def test_main_exits(monkeypatch: MonkeyPatch, capsys: CaptureFixture[str]) -> None:
    import src.main.main as main_module

    class FakeConfig:
        system_prompt = None

    monkeypatch.setattr(main_module, 'load_config', lambda: FakeConfig())
    monkeypatch.setattr(main_module, 'LLMClient', lambda config: object())
    monkeypatch.setattr(main_module, 'MessageHistory', lambda config: object())
    monkeypatch.setattr(main_module, 'print_start_menu', lambda: None)

    inputs = iter(['\\q'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    main_module.main()

    captured = capsys.readouterr()

    assert 'Bye!' in captured.out


def test_main_handles_config_error(
    monkeypatch: MonkeyPatch,
    capsys: CaptureFixture[str],
) -> None:
    import src.main.main as main_module

    def raise_error() -> Any:
        raise ValueError('bad config')

    monkeypatch.setattr(main_module, 'load_config', raise_error)

    main_module.main()

    captured = capsys.readouterr()

    assert 'Config error: bad config' in captured.out
