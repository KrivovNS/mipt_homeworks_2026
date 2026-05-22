from src.main.config import AppConfig
from src.main.llm_client import LLMClient, convert_messages
from src.main.models import ChatMessage


def make_config() -> AppConfig:
    return AppConfig(
        api_key="test",
        api_host="http://localhost:11434/v1/",
        model="test-model",
        limit_message=20,
        limit_characters=2000,
        temperature=0.3,
        system_prompt=None,
    )


def test_convert_messages() -> None:
    messages = [
        ChatMessage(role="user", content="hello"),
        ChatMessage(role="assistant", content="hi"),
    ]

    assert convert_messages(messages) == [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "hi"},
    ]


def test_llm_client_generate(monkeypatch) -> None:
    import src.main.llm_client as llm_module

    class FakeMessage:
        content = "fake answer"

    class FakeChoice:
        message = FakeMessage()

    class FakeCompletion:
        choices = [FakeChoice()]

    class FakeCompletions:
        def create(self, **kwargs):
            assert kwargs["model"] == "test-model"
            assert kwargs["temperature"] == 0.3
            assert kwargs["messages"] == [{"role": "user", "content": "hello"}]
            return FakeCompletion()

    class FakeChat:
        completions = FakeCompletions()

    class FakeOpenAI:
        def __init__(self, api_key: str, base_url: str) -> None:
            assert api_key == "test"
            assert base_url == "http://localhost:11434/v1/"

        chat = FakeChat()

    monkeypatch.setattr(llm_module, "OpenAI", FakeOpenAI)

    client = LLMClient(make_config())

    assert client.generate([ChatMessage(role="user", content="hello")]) == "fake answer"