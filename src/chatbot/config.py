"""Configuration module for the chatbot application."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import ClassVar


@dataclass(frozen=True)
class OllamaConfig:
    """Configuration for Ollama connection."""

    base_url: str = field(
        default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    )
    timeout: int = field(
        default_factory=lambda: int(os.getenv("OLLAMA_TIMEOUT", "120"))
    )


@dataclass(frozen=True)
class ModelConfig:
    """Configuration for available models."""

    AVAILABLE_MODELS: ClassVar[list[str]] = [
        "deepseek-r1:14b",
        "ministral-3:14b",
        "devstral-small-2:latest",
    ]

    REASONING_MODELS: ClassVar[set[str]] = {"deepseek-r1:14b"}

    @classmethod
    def get_default_model(cls) -> str:
        """Get the default model."""
        return cls.AVAILABLE_MODELS[0]

    @classmethod
    def supports_reasoning(cls, model_name: str) -> bool:
        """Check if a model supports reasoning/thinking."""
        return model_name in cls.REASONING_MODELS


@dataclass(frozen=True)
class UIConfig:
    """Configuration for the UI."""

    app_title: str = "Ollama Chat"
    app_description: str = "A sleek interface for local LLM conversations"
    chat_height: int = 550
    max_message_length: int = 10000


# Global configuration instances
ollama_config = OllamaConfig()
model_config = ModelConfig()
ui_config = UIConfig()
