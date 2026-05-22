from dataclasses import dataclass
from typing import Literal

Role = Literal["user", "assistant", "system"]

@dataclass
class ChatMessage:
    role: Role
    content: str