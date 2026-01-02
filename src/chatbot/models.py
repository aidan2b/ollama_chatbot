"""Data models for the chatbot application."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Literal


class MessageRole(str, Enum):
    """Role of a message sender."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class ChatMessage:
    """A single chat message."""

    role: Literal["user", "assistant"]
    content: str

    def to_dict(self) -> dict[str, str]:
        """Convert to dictionary format for Gradio."""
        return {"role": self.role, "content": self.content}

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> ChatMessage:
        """Create from dictionary."""
        return cls(
            role=data.get("role", "user"),  # type: ignore[arg-type]
            content=data.get("content", ""),
        )


@dataclass
class ChatHistory:
    """Container for chat history."""

    messages: list[ChatMessage]

    def __init__(self, messages: list[ChatMessage] | None = None) -> None:
        self.messages = messages or []

    def add_user_message(self, content: str) -> None:
        """Add a user message."""
        self.messages.append(ChatMessage(role="user", content=content))

    def add_assistant_message(self, content: str) -> None:
        """Add an assistant message."""
        self.messages.append(ChatMessage(role="assistant", content=content))

    def to_list(self) -> list[dict[str, str]]:
        """Convert to list of dictionaries for Gradio."""
        return [msg.to_dict() for msg in self.messages]

    @classmethod
    def from_list(cls, data: list[dict[str, str]]) -> ChatHistory:
        """Create from list of dictionaries."""
        return cls([ChatMessage.from_dict(msg) for msg in data])

    def clear(self) -> None:
        """Clear all messages."""
        self.messages.clear()

    def __len__(self) -> int:
        return len(self.messages)
