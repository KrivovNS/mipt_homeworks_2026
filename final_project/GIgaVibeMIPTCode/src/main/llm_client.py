from collections.abc import Iterator

from openai import OpenAI

from .config import AppConfig
from .models import ChatMessage


def convert_messages(messages: list[ChatMessage]) -> list[dict[str, str]]:
    return [
        {
            "role": message.role,
            "content": message.content,
        }
        for message in messages
    ]


class LLMClient:
    def __init__(self, config: AppConfig) -> None:
        self._config = config
        self._client = OpenAI(
            api_key=config.api_key,
            base_url=config.api_host,
        )

    def generate(self, messages: list[ChatMessage]) -> str:
        completion = self._client.chat.completions.create(
            model=self._config.model,
            messages=convert_messages(messages),
            temperature=self._config.temperature,
        )

        content = completion.choices[0].message.content

        if content is None:
            return ""

        return content

    def generate_stream(self, messages: list[ChatMessage]) -> Iterator[str]:
        stream = self._client.chat.completions.create(
            model=self._config.model,
            messages=convert_messages(messages),
            temperature=self._config.temperature,
            stream=True,
        )

        for chunk in stream:
            content = chunk.choices[0].delta.content

            if content is not None:
                yield content