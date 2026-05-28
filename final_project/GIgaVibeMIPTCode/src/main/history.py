from collections import deque

from .config import AppConfig
from .models import ChatMessage


class MessageHistory:
    def __init__(self, config: AppConfig) -> None:
        self._config = config
        self._history: deque[ChatMessage] = deque()
        self._message_count = 0
        self._char_count = 0

    def delete_oldest_message(self) -> None:
        deleted_message = self._history.popleft()
        self._message_count -= 1
        self._char_count -= len(deleted_message.content)

    def add_message(self, message: ChatMessage) -> None:
        self._history.append(message)
        self._message_count += 1
        self._char_count += len(message.content)
        self._trim_history()

    def get_history(self) -> list[ChatMessage]:
        return list(self._history)

    def get_history_with_system_prompt(
        self,
        system_prompt: str | None,
    ) -> list[ChatMessage]:
        messages = self.get_history()

        if system_prompt is None:
            return messages

        return [
            ChatMessage(role='system', content=system_prompt),
            *messages,
        ]

    def clear(self) -> None:
        self._history.clear()
        self._message_count = 0
        self._char_count = 0

    def _trim_history(self) -> None:
        while self._is_message_limit_exceeded() or self._is_char_limit_exceeded():
            if self._message_count == 1:
                self._trim_single_message()
                return

            self.delete_oldest_message()

    def _is_message_limit_exceeded(self) -> bool:
        return (
            self._config.limit_message is not None
            and self._message_count > self._config.limit_message
        )

    def _is_char_limit_exceeded(self) -> bool:
        return (
            self._config.limit_characters is not None
            and self._char_count > self._config.limit_characters
        )

    def _trim_single_message(self) -> None:
        if self._config.limit_characters is None:
            return

        message = self._history[0]
        message.content = message.content[-self._config.limit_characters :]
        self._char_count = len(message.content)
