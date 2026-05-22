from src.main.config import AppConfig
from src.main.history import MessageHistory
from src.main.models import ChatMessage


def make_config(limit_message: int | None = None, limit_characters: int | None = None) -> AppConfig:
    return AppConfig(
        api_key='test',
        api_host='http://localhost:11434/v1/',
        model='test-model',
        limit_message=limit_message,
        limit_characters=limit_characters,
        temperature=0.3,
        system_prompt=None,
    )


def test_history_adds_messages() -> None:
    history = MessageHistory(make_config())

    history.add_message(ChatMessage(role='user', content='hello'))

    assert history.get_history() == [ChatMessage(role='user', content='hello')]


def test_history_limits_message_count() -> None:
    history = MessageHistory(make_config(limit_message=2))

    history.add_message(ChatMessage(role='user', content='first'))
    history.add_message(ChatMessage(role='assistant', content='second'))
    history.add_message(ChatMessage(role='user', content='third'))

    assert history.get_history() == [
        ChatMessage(role='assistant', content='second'),
        ChatMessage(role='user', content='third'),
    ]


def test_history_limits_characters_by_deleting_old_messages() -> None:
    history = MessageHistory(make_config(limit_characters=10))

    history.add_message(ChatMessage(role='user', content='12345'))
    history.add_message(ChatMessage(role='assistant', content='67890'))
    history.add_message(ChatMessage(role='user', content='abc'))

    assert history.get_history() == [
        ChatMessage(role='assistant', content='67890'),
        ChatMessage(role='user', content='abc'),
    ]


def test_history_trims_single_large_message() -> None:
    history = MessageHistory(make_config(limit_characters=5))

    history.add_message(ChatMessage(role='user', content='123456789'))

    assert history.get_history() == [
        ChatMessage(role='user', content='56789'),
    ]


def test_history_clear() -> None:
    history = MessageHistory(make_config())

    history.add_message(ChatMessage(role='user', content='hello'))
    history.clear()

    assert history.get_history() == []